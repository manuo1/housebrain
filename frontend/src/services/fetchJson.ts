interface FetchError extends Error {
  status?: number;
}

export async function fetchJson<T = unknown>(url: string): Promise<T> {
  try {
    const res = await fetch(url);

    if (!res.ok) {
      const err: FetchError = new Error(`HTTP error! Status: ${res.status}`);
      err.status = res.status;
      console.error(`HTTP error while fetching ${url}: ${res.status} ${res.statusText}`);
      throw err;
    }
    return await res.json();
  } catch (err) {
    const fetchErr = err as FetchError;
    if (fetchErr.status === undefined) {
      fetchErr.status = 0;
      console.error(`Network error or no response from ${url} : ${fetchErr}`);
    }
    throw fetchErr;
  }
}
