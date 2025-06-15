export async function fetchJson(url) {
  try {
    const res = await fetch(url);

    if (!res.ok) {
      const err = new Error(`HTTP error! Status: ${res.status}`);
      err.status = res.status;
      console.error(
        `HTTP error while fetching ${url}: ${res.status} ${res.statusText}`
      );
      throw err;
    }
    console.log(res);
    return await res.json();
  } catch (err) {
    if (err.status === undefined) {
      err.status = 0;
      console.error(`Network error or no response from ${url} : ${err}`);
    }
    throw err;
  }
}
