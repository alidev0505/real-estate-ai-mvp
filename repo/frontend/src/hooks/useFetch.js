import { useEffect, useState } from 'react'
export default function useFetch(fn, deps = []) {
  const [data, setData] = useState(null); const [error, setError] = useState('')
  useEffect(() => { let on = true; fn().then((d) => on && setData(d)).catch((e) => on && setError(e.message)); return () => { on = false } }, deps) // eslint-disable-line
  return { data, error, loading: !data && !error }
}
