import { useState, useEffect } from 'react';
import { api } from '../utils/api';

export function useRecommend() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const submit = async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.recommend(payload);
      setData(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, submit };
}

export function useWeather(district) {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  useEffect(() => {
    if (!district) return;
    setLoading(true);
    api.weather(district, 15)
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [district]);

  return { data, loading, error };
}

export function useDistricts() {
  const [districts, setDistricts] = useState([]);
  useEffect(() => {
    api.districts().then(r => setDistricts(r.districts)).catch(() => {});
  }, []);
  return districts;
}

export function useTaluks(district) {
  const [taluks, setTaluks] = useState([]);
  useEffect(() => {
    if (!district) { setTaluks([]); return; }
    api.taluks(district).then(r => setTaluks(r.taluks)).catch(() => {});
  }, [district]);
  return taluks;
}

export function useHealth() {
  const [health, setHealth] = useState(null);
  useEffect(() => {
    const check = () => api.health().then(setHealth).catch(() => setHealth({ status: 'offline' }));
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);
  return health;
}
