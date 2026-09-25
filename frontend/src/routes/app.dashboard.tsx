import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState, useRef } from "react";
import {
  Sprout, Leaf, BarChart3, Database, ArrowRight, Activity, Server, History,
  UploadCloud, Eye, Download, Trash2, FileSpreadsheet, Loader2, RefreshCw, Layers
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MetricCard } from "@/components/opticrop/MetricCard";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { useAuth } from "../lib/auth";
import { api, PredictionRunRecord, DatasetRecord, DatasetPreviewData, getStoredToken } from "../lib/api";
import { toast } from "sonner";

export const Route = createFileRoute("/app/dashboard")({
  component: Dashboard,
});

const quickActions = [
  { to: "/app/recommendation", icon: Sprout, title: "Crop Recommendation", desc: "Predict the best crop for your field." },
  { to: "/app/suitability", icon: Leaf, title: "Suitability Checker", desc: "Check how well a crop fits conditions." },
  { to: "/app/analytics", icon: BarChart3, title: "Analytics", desc: "Explore dataset patterns & insights." },
] as const;

function Dashboard() {
  const { user } = useAuth();
  const [predictions, setPredictions] = useState<PredictionRunRecord[]>([]);
  const [datasets, setDatasets] = useState<DatasetRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [datasetsLoading, setDatasetsLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dbHealthy, setDbHealthy] = useState<boolean | null>(null);

  // Preview modal state
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewDataset, setPreviewDataset] = useState<DatasetRecord | null>(null);
  const [previewData, setPreviewData] = useState<DatasetPreviewData | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const loadDatasets = async () => {
    try {
      setDatasetsLoading(true);
      const res = await api.datasets.list();
      setDatasets(res.items || []);
    } catch (err: any) {
      console.error("Failed to load datasets:", err);
    } finally {
      setDatasetsLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;

    async function loadDashboardData() {
      setIsLoading(true);
      try {
        const [historyRes, healthRes, datasetsRes] = await Promise.allSettled([
          api.predictions.history(),
          api.health.check(),
          api.datasets.list(),
        ]);

        if (mounted && historyRes.status === "fulfilled") {
          setPredictions(historyRes.value || []);
        }
        if (mounted && healthRes.status === "fulfilled") {
          setDbHealthy(healthRes.value.status === "healthy");
        }
        if (mounted && datasetsRes.status === "fulfilled") {
          setDatasets(datasetsRes.value.items || []);
        }
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      } finally {
        if (mounted) {
          setIsLoading(false);
          setDatasetsLoading(false);
        }
      }
    }

    loadDashboardData();
    return () => {
      mounted = false;
    };
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".csv")) {
      toast.error("Please select a valid CSV file (.csv)");
      return;
    }

    setUploading(true);
    try {
      await api.datasets.upload(file, "Uploaded from Dashboard");
      toast.success(`Dataset "${file.name}" uploaded successfully!`);
      await loadDatasets();
    } catch (err: any) {
      toast.error(err.message || "Failed to upload dataset.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleOpenPreview = async (dataset: DatasetRecord) => {
    setPreviewDataset(dataset);
    setPreviewOpen(true);
    setPreviewLoading(true);
    setPreviewData(null);

    try {
      const data = await api.datasets.preview(dataset.id);
      setPreviewData(data);
    } catch (err: any) {
      toast.error(err.message || "Failed to load CSV preview.");
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleDownloadDataset = async (dataset: DatasetRecord) => {
    try {
      const token = getStoredToken();
      const res = await fetch(api.datasets.getDownloadUrl(dataset.id), {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error(`Download failed with status ${res.status}`);
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = dataset.original_filename || `${dataset.name}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success(`Downloaded "${dataset.original_filename || dataset.name}"`);
    } catch (err: any) {
      toast.error(err.message || "Failed to download dataset.");
    }
  };

  const handleDeleteDataset = async (dataset: DatasetRecord) => {
    if (!confirm(`Are you sure you want to delete "${dataset.original_filename || dataset.name}"?`)) {
      return;
    }

    try {
      await api.datasets.delete(dataset.id);
      toast.success("Dataset deleted successfully.");
      await loadDatasets();
    } catch (err: any) {
      toast.error(err.message || "Failed to delete dataset.");
    }
  };

  function formatBytes(bytes: number) {
    if (!bytes || bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
  }

  const kpiCards = [
    {
      icon: Database,
      label: "Database Source",
      value: "MongoDB Atlas",
      sub: dbHealthy ? "Cluster Online" : "Connecting...",
      trend: "live",
    },
    {
      icon: History,
      label: "Predictions Recorded",
      value: predictions.length.toString(),
      sub: "persistent records",
      trend: predictions.length > 0 ? `+${predictions.length}` : "empty",
    },
    {
      icon: FileSpreadsheet,
      label: "Uploaded Datasets",
      value: datasets.length.toString(),
      sub: "CSV files in Atlas",
      trend: datasets.length > 0 ? `+${datasets.length}` : "empty",
    },
    {
      icon: Server,
      label: "Backend Service",
      value: "FastAPI",
      sub: "MongoDB Motor + Beanie",
      trend: "active",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Hero banner */}
      <Card className="animate-fade-up glass relative overflow-hidden rounded-[20px] border-border/60 p-7 shadow-[var(--shadow-soft)] md:p-9">
        <div className="pointer-events-none absolute -right-10 -top-10 h-56 w-56 rounded-full bg-primary/15 blur-3xl" />
        <div className="relative">
          <Badge variant="secondary" className="rounded-full">
            <Activity className="mr-1 h-3.5 w-3.5" />
            {dbHealthy ? "MongoDB Atlas Connected" : "Connecting to Database..."}
          </Badge>
          <h1 className="mt-4 font-display text-3xl font-800 tracking-tight md:text-4xl">
            Welcome back{user?.fullName ? `, ${user.fullName}` : ""}! 🌱
          </h1>
          <p className="mt-2 max-w-xl text-muted-foreground">
            Your OptiCrop agricultural intelligence workspace is connected directly to MongoDB Atlas.
          </p>

          <div className="mt-4 grid gap-2 sm:flex sm:gap-6 text-xs text-muted-foreground border-t border-border/40 pt-4 max-w-xl">
            <div><span className="font-600 text-foreground">Role:</span> {user?.role || "Farmer"}</div>
            {user?.email && <div><span className="font-600 text-foreground">Account:</span> {user.email}</div>}
            {user?.location && <div><span className="font-600 text-foreground">Location:</span> {user.location}</div>}
            {user?.registrationDate && <div><span className="font-600 text-foreground">Member Since:</span> {user.registrationDate}</div>}
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <Button asChild variant="hero"><Link to="/app/recommendation"><Sprout className="h-4 w-4" /> Predict Crop</Link></Button>
            <Button asChild variant="outline"><Link to="/app/suitability"><Leaf className="h-4 w-4" /> Analyze Soil</Link></Button>
          </div>
        </div>
      </Card>

      {/* Real KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {kpiCards.map((k) => (
          <MetricCard key={k.label} {...k} />
        ))}
      </div>

      {/* Quick actions */}
      <div>
        <h2 className="mb-3 font-display text-lg font-600">Quick Actions</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {quickActions.map((a) => (
            <Link key={a.to} to={a.to}>
              <Card className="card-lift group flex h-full items-center gap-4 rounded-[20px] border-border/70 p-5 shadow-[var(--shadow-soft)]">
                <span className="grid h-12 w-12 place-items-center rounded-xl bg-primary/10 text-primary">
                  <a.icon className="h-6 w-6" />
                </span>
                <div className="flex-1">
                  <p className="font-display font-600">{a.title}</p>
                  <p className="text-sm text-muted-foreground">{a.desc}</p>
                </div>
                <ArrowRight className="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Agricultural Datasets (CSV) section with Upload and Interactive Preview */}
      <Card className="overflow-hidden rounded-[20px] border-border/70 shadow-[var(--shadow-soft)]">
        <div className="flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between border-b border-border/60">
          <div>
            <div className="flex items-center gap-2">
              <FileSpreadsheet className="h-5 w-5 text-primary" />
              <h2 className="font-display text-lg font-600">Agricultural Datasets (CSV)</h2>
              <Badge variant="secondary" className="rounded-full text-xs">
                {datasets.length} {datasets.length === 1 ? "dataset" : "datasets"}
              </Badge>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Upload CSV datasets, inspect field records, and view environmental parameters persisted in MongoDB Atlas GridFS.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="file"
              ref={fileInputRef}
              accept=".csv,text/csv"
              className="hidden"
              onChange={handleFileUpload}
            />
            <Button
              variant="default"
              size="sm"
              disabled={uploading}
              onClick={() => fileInputRef.current?.click()}
              className="rounded-xl shadow-sm"
            >
              {uploading ? (
                <>
                  <Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> Uploading CSV...
                </>
              ) : (
                <>
                  <UploadCloud className="mr-1.5 h-4 w-4" /> Upload CSV Dataset
                </>
              )}
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8 rounded-lg"
              onClick={loadDatasets}
              disabled={datasetsLoading}
              title="Refresh datasets"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${datasetsLoading ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>

        <div className="overflow-x-auto">
          {datasetsLoading && datasets.length === 0 ? (
            <div className="py-10 text-center text-sm text-muted-foreground flex items-center justify-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-primary" /> Loading datasets from MongoDB Atlas...
            </div>
          ) : datasets.length === 0 ? (
            <div className="py-12 text-center">
              <FileSpreadsheet className="mx-auto h-9 w-9 text-muted-foreground/40 mb-2" />
              <p className="font-display font-600 text-foreground">No datasets uploaded yet</p>
              <p className="text-xs text-muted-foreground mt-1 max-w-sm mx-auto">
                Upload your agricultural CSV files (such as soil samples or crop recommendation data) to view records and run analytics.
              </p>
              <Button
                variant="outline"
                size="sm"
                className="mt-4"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
              >
                <UploadCloud className="mr-1.5 h-3.5 w-3.5" /> Upload Your First CSV
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-border/60">
                  <TableHead>Dataset Name</TableHead>
                  <TableHead>Dimensions</TableHead>
                  <TableHead>File Size</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Uploaded At</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {datasets.map((d) => (
                  <TableRow key={d.id} className="border-border/60 hover:bg-muted/30 transition-colors">
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary/10 text-primary">
                          <FileSpreadsheet className="h-4 w-4" />
                        </span>
                        <div>
                          <p className="font-600 text-foreground text-sm leading-tight">
                            {d.original_filename || d.name}
                          </p>
                          <p className="font-mono text-[11px] text-muted-foreground">{d.name}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-xs font-mono text-muted-foreground">
                      {d.rows && d.columns ? `${d.rows} rows × ${d.columns} cols` : "Parsed"}
                    </TableCell>
                    <TableCell className="text-xs font-mono text-muted-foreground">
                      {formatBytes(d.size)}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          d.status === "READY_FOR_TRAINING" || d.status === "VALIDATED"
                            ? "secondary"
                            : "outline"
                        }
                        className="rounded-full text-[11px]"
                      >
                        {d.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-xs text-muted-foreground">
                      {new Date(d.uploaded_at).toLocaleDateString(undefined, {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <Button
                          variant="default"
                          size="sm"
                          className="h-8 gap-1 rounded-lg px-2.5 text-xs"
                          onClick={() => handleOpenPreview(d)}
                        >
                          <Eye className="h-3.5 w-3.5" /> Open / View CSV
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          className="h-8 w-8 rounded-lg"
                          title="Download CSV"
                          onClick={() => handleDownloadDataset(d)}
                        >
                          <Download className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 rounded-lg text-destructive hover:bg-destructive/10 hover:text-destructive"
                          title="Delete dataset"
                          onClick={() => handleDeleteDataset(d)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </Card>

      {/* Interactive CSV Preview Modal */}
      <Dialog open={previewOpen} onOpenChange={setPreviewOpen}>
        <DialogContent className="max-w-5xl max-h-[88vh] flex flex-col p-6 overflow-hidden rounded-[20px]">
          <DialogHeader className="pb-3 border-b border-border/60">
            <div className="flex items-center gap-2">
              <span className="grid h-9 w-9 place-items-center rounded-xl bg-primary/10 text-primary">
                <FileSpreadsheet className="h-5 w-5" />
              </span>
              <div>
                <DialogTitle className="text-xl font-display font-700">
                  {previewDataset?.original_filename || previewDataset?.name || "Dataset Preview"}
                </DialogTitle>
                <DialogDescription className="text-xs text-muted-foreground">
                  Interactive data view from persistent storage in MongoDB Atlas
                </DialogDescription>
              </div>
            </div>
          </DialogHeader>

          {previewLoading ? (
            <div className="flex h-72 flex-col items-center justify-center gap-3">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground">Streaming dataset preview from storage...</p>
            </div>
          ) : !previewData || !previewData.data || previewData.data.length === 0 ? (
            <div className="py-12 text-center">
              <p className="text-sm text-muted-foreground">No preview records available for this dataset.</p>
            </div>
          ) : (
            <div className="flex flex-col flex-1 overflow-hidden space-y-3">
              {/* Dimensions and Schema Stats */}
              <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-muted/40 p-3 text-xs">
                <div className="flex items-center gap-3">
                  <div>
                    <span className="text-muted-foreground">Total Rows: </span>
                    <span className="font-600 font-mono text-foreground">{previewData.shape[0]}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Columns: </span>
                    <span className="font-600 font-mono text-foreground">{previewData.shape[1]}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Memory: </span>
                    <span className="font-600 font-mono text-foreground">
                      {formatBytes(previewData.memory_usage_bytes)}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 flex-wrap">
                  {previewData.columns.map((col) => (
                    <Badge key={col} variant="outline" className="font-mono text-[11px] px-1.5 py-0 bg-background">
                      {col}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Scrollable Data Table */}
              <div className="flex-1 overflow-auto rounded-xl border border-border/70 bg-card">
                <Table>
                  <TableHeader className="sticky top-0 bg-muted/95 backdrop-blur z-10">
                    <TableRow className="border-border/60">
                      <TableHead className="w-12 text-center text-xs font-mono">#</TableHead>
                      {previewData.columns.map((col) => (
                        <TableHead key={col} className="text-xs font-600 whitespace-nowrap">
                          {col}
                          {previewData.dtypes[col] && (
                            <span className="ml-1 text-[10px] font-mono text-muted-foreground font-normal">
                              ({previewData.dtypes[col]})
                            </span>
                          )}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {previewData.data.map((row, idx) => (
                      <TableRow key={idx} className="border-border/40 hover:bg-muted/20 text-xs">
                        <TableCell className="text-center font-mono text-muted-foreground text-[11px]">
                          {idx + 1}
                        </TableCell>
                        {previewData.columns.map((col) => {
                          const val = row[col];
                          const isNumeric = typeof val === "number";
                          return (
                            <TableCell key={col} className={`whitespace-nowrap ${isNumeric ? "font-mono" : ""}`}>
                              {val === null || val === undefined ? (
                                <span className="text-muted-foreground/50 italic">null</span>
                              ) : isNumeric ? (
                                Number.isInteger(val) ? val : Number(val.toFixed(2))
                              ) : (
                                String(val)
                              )}
                            </TableCell>
                          );
                        })}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Modal footer summary */}
              <div className="flex items-center justify-between pt-2 text-xs text-muted-foreground">
                <p>
                  Showing first {Math.min(previewData.data.length, 100)} of {previewData.shape[0]} records
                </p>
                {previewDataset && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 text-xs"
                    onClick={() => handleDownloadDataset(previewDataset)}
                  >
                    <Download className="mr-1 h-3 w-3" /> Download Full CSV
                  </Button>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Persistent predictions from MongoDB Atlas */}
      <Card className="overflow-hidden rounded-[20px] border-border/70 shadow-[var(--shadow-soft)]">
        <div className="flex items-center justify-between p-5">
          <h2 className="font-display text-lg font-600">Recent Predictions</h2>
          <Button asChild variant="ghost" size="sm"><Link to="/app/analytics">View all <ArrowRight className="h-4 w-4" /></Link></Button>
        </div>
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="py-12 text-center text-sm text-muted-foreground">
              Loading predictions from MongoDB Atlas...
            </div>
          ) : predictions.length === 0 ? (
            <div className="py-12 text-center">
              <Sprout className="mx-auto h-9 w-9 text-muted-foreground/40 mb-2" />
              <p className="font-display font-600 text-foreground">No predictions recorded yet</p>
              <p className="text-xs text-muted-foreground mt-1 max-w-sm mx-auto">
                No prediction runs found in your MongoDB Atlas database. Run a crop recommendation to record your first prediction.
              </p>
              <Button asChild variant="outline" size="sm" className="mt-4">
                <Link to="/app/recommendation"><Sprout className="mr-1.5 h-3.5 w-3.5" /> Start First Prediction</Link>
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-border/60">
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Predicted Crop</TableHead>
                  <TableHead className="text-right">Execution Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {predictions.map((r) => (
                  <TableRow key={r.id} className="border-border/60">
                    <TableCell className="whitespace-nowrap text-muted-foreground">
                      {new Date(r.prediction_timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge variant={r.status === "COMPLETED" ? "secondary" : "outline"} className="rounded-full">
                        {r.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {r.predictions && r.predictions.length > 0 ? (
                        <span className="font-600 text-foreground">{r.predictions.join(", ")}</span>
                      ) : (
                        <span className="text-muted-foreground italic">None</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right font-mono text-xs text-muted-foreground">
                      {(r.execution_time * 1000).toFixed(1)} ms
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </Card>
    </div>
  );
}
