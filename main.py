
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import heapq

app = FastAPI(title="Network Route Optimization API")

nodes = {}
edges = []
history = []

class NodeRequest(BaseModel):
    name: str

class EdgeRequest(BaseModel):
    source: str
    destination: str
    latency: float = Field(gt=0)

class RouteRequest(BaseModel):
    source: str
    destination: str

@app.post("/nodes", status_code=201)
def add_node(data: NodeRequest):
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")

    if data.name in nodes.values():
        raise HTTPException(status_code=400, detail="Duplicate node")

    node_id = len(nodes) + 1
    nodes[node_id] = data.name

    return {
        "id": node_id,
        "name": data.name
    }

@app.get("/nodes")
def get_nodes():
    return [{"id": k, "name": v} for k, v in nodes.items()]

@app.delete("/nodes/{node_id}")
def delete_node(node_id: int):
    if node_id not in nodes:
        raise HTTPException(status_code=404, detail="Node not found")

    node_name = nodes[node_id]

    global edges
    edges = [
        edge for edge in edges
        if edge["source"] != node_name and edge["destination"] != node_name
    ]

    del nodes[node_id]

    return {"message": "Node deleted successfully"}

@app.post("/edges", status_code=201)
def add_edge(data: EdgeRequest):
    if data.source == data.destination:
        raise HTTPException(status_code=400, detail="Source and destination cannot be same")

    if data.source not in nodes.values() or data.destination not in nodes.values():
        raise HTTPException(status_code=400, detail="Nodes not found")

    for edge in edges:
        if (
            edge["source"] == data.source and
            edge["destination"] == data.destination
        ):
            raise HTTPException(status_code=400, detail="Duplicate edge")

    edge_id = len(edges) + 1

    edge = {
        "id": edge_id,
        "source": data.source,
        "destination": data.destination,
        "latency": data.latency
    }

    edges.append(edge)

    return edge

@app.get("/edges")
def get_edges():
    return edges

@app.delete("/edges/{edge_id}")
def delete_edge(edge_id: int):
    for edge in edges:
        if edge["id"] == edge_id:
            edges.remove(edge)
            return {"message": "Edge deleted successfully"}

    raise HTTPException(status_code=404, detail="Edge not found")

def build_graph():
    graph = {}

    for node in nodes.values():
        graph[node] = []

    for edge in edges:
        graph[edge["source"]].append(
            (edge["destination"], edge["latency"])
        )

    return graph

def dijkstra(graph, start, end):
    pq = [(0, start, [])]
    visited = set()

    while pq:
        total_latency, current, path = heapq.heappop(pq)

        if current in visited:
            continue

        visited.add(current)
        path = path + [current]

        if current == end:
            return total_latency, path

        for neighbor, weight in graph.get(current, []):
            if neighbor not in visited:
                heapq.heappush(
                    pq,
                    (total_latency + weight, neighbor, path)
                )

    return None, None

@app.post("/routes/shortest")
def shortest_route(data: RouteRequest):
    if data.source not in nodes.values() or data.destination not in nodes.values():
        raise HTTPException(status_code=400, detail="Invalid nodes")

    graph = build_graph()

    total_latency, path = dijkstra(
        graph,
        data.source,
        data.destination
    )

    if not path:
        raise HTTPException(
            status_code=404,
            detail=f"No path exists between {data.source} and {data.destination}"
        )

    record = {
        "id": len(history) + 1,
        "source": data.source,
        "destination": data.destination,
        "total_latency": total_latency,
        "path": path,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    history.append(record)

    return {
        "total_latency": total_latency,
        "path": path
    }

@app.get("/routes/history")
def route_history(
    source: Optional[str] = None,
    destination: Optional[str] = None,
    limit: Optional[int] = Query(default=None, gt=0),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    result = history

    if source:
        result = [r for r in result if r["source"] == source]

    if destination:
        result = [r for r in result if r["destination"] == destination]

    if date_from:
        result = [
            r for r in result
            if r["created_at"] >= date_from
        ]

    if date_to:
        result = [
            r for r in result
            if r["created_at"] <= date_to
        ]

    if limit:
        result = result[:limit]

    return result
