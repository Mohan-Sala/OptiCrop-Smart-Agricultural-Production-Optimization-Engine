from typing import List, Dict, Any
from app.models.dataset import Dataset


class LineageGraphService:
    """Builds a Directed Acyclic Graph (DAG) representing dataset stages and version lineages."""

    def build_lineage_dag(self, datasets: List[Dataset]) -> Dict[str, List[Dict[str, Any]]]:
        nodes = []
        edges = []
        
        for ds in datasets:
            nodes.append({
                "id": str(ds.id),
                "label": f"{ds.name} (v{ds.version})",
                "type": ds.dataset_stage.name if hasattr(ds.dataset_stage, "name") else str(ds.dataset_stage),
                "version": ds.version,
                "metadata": {
                    "rows": ds.rows,
                    "columns": ds.columns,
                    "size_bytes": ds.size,
                    "status": ds.status.name if hasattr(ds.status, "name") else str(ds.status),
                }
            })
            
            if ds.parent_dataset_id:
                edges.append({
                    "id": f"edge_{ds.parent_dataset_id}_{ds.id}",
                    "source": str(ds.parent_dataset_id),
                    "target": str(ds.id),
                    "relationship": "preprocessed"
                })
                
        return {"nodes": nodes, "edges": edges}
