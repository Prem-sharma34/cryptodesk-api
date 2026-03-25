"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api, { getAccessToken, setAccessToken } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [watchlist, setWatchlist] = useState([]);
  const [assets, setAssets] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const init = async () => {
      try {
        // If no in-memory token, try refreshing first
        if (!getAccessToken()) {
          const refreshToken = document.cookie
            .split("; ").find((r) => r.startsWith("refresh_token="))?.split("=")[1];
          if (!refreshToken) { router.push("/login"); return; }

          const { data } = await api.post("/auth/refresh", { refresh_token: refreshToken });
          setAccessToken(data.access_token);
          document.cookie = `refresh_token=${data.refresh_token}; path=/; max-age=${7 * 24 * 3600}; SameSite=Strict`;
        }

        const [meRes, watchlistRes, assetsRes] = await Promise.all([
          api.get("/auth/me"),
          api.get("/watchlist/"),
          api.get("/assets/"),
        ]);

        setUser(meRes.data);
        setWatchlist(watchlistRes.data);
        setAssets(assetsRes.data);
      } catch {
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  const addToWatchlist = async () => {
    if (!selectedAsset) return;
    setError("");
    try {
      const { data } = await api.post("/watchlist/", { asset_id: selectedAsset, notes });
      setWatchlist([...watchlist, data]);
      setNotes("");
      setSelectedAsset("");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to add asset");
    }
  };

  const removeFromWatchlist = async (itemId) => {
    await api.delete(`/watchlist/${itemId}`);
    setWatchlist(watchlist.filter((i) => i.id !== itemId));
  };

  const handleLogout = async () => {
    const refreshToken = document.cookie
      .split("; ").find((r) => r.startsWith("refresh_token="))?.split("=")[1];
    if (refreshToken) await api.post("/auth/logout", { refresh_token: refreshToken }).catch(() => {});
    setAccessToken(null);
    document.cookie = "refresh_token=; max-age=0";
    router.push("/login");
  };

  if (loading) return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center text-white text-lg">
      Loading...
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-blue-400">CryptoDesk</h1>
            <p className="text-gray-400 text-sm mt-1">Welcome, {user?.username}</p>
          </div>
          <button onClick={handleLogout}
            className="text-sm text-gray-400 hover:text-red-400 transition">
            Logout
          </button>
        </div>

        {/* Add to Watchlist */}
        <div className="bg-gray-900 rounded-xl p-5 mb-6">
          <h2 className="text-lg font-semibold mb-3">Add to Watchlist</h2>
          {error && <p className="text-red-400 text-sm mb-3">{error}</p>}
          <div className="flex gap-3 flex-wrap">
            <select value={selectedAsset} onChange={(e) => setSelectedAsset(e.target.value)}
              className="bg-gray-800 text-white rounded-lg px-3 py-2 flex-1 min-w-[150px] outline-none">
              <option value="">Select asset</option>
              {assets.map((a) => (
                <option key={a.id} value={a.id}>{a.symbol} — {a.name}</option>
              ))}
            </select>
            <input placeholder="Notes (optional)" value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="bg-gray-800 text-white rounded-lg px-3 py-2 flex-1 min-w-[150px] outline-none" />
            <button onClick={addToWatchlist}
              className="bg-blue-600 hover:bg-blue-700 px-5 py-2 rounded-lg font-semibold transition">
              Add
            </button>
          </div>
        </div>

        {/* Watchlist */}
        <div className="bg-gray-900 rounded-xl p-5">
          <h2 className="text-lg font-semibold mb-4">My Watchlist</h2>
          {watchlist.length === 0 ? (
            <p className="text-gray-500 text-sm">No assets yet. Add one above.</p>
          ) : (
            <div className="space-y-3">
              {watchlist.map((item) => (
                <div key={item.id} className="flex justify-between items-center bg-gray-800 rounded-lg px-4 py-3">
                  <div>
                    <span className="font-bold text-blue-300">{item.asset.symbol}</span>
                    <span className="text-gray-300 ml-2 text-sm">{item.asset.name}</span>
                    {item.notes && <p className="text-gray-500 text-xs mt-0.5">{item.notes}</p>}
                  </div>
                  <button onClick={() => removeFromWatchlist(item.id)}
                    className="text-red-400 hover:text-red-300 text-sm transition">
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}