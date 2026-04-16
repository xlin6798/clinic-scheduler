export function parsePatientQuery(query) {
  if (!query) {
    return {
      name: "",
      date_of_birth: "",
      chart_number: "",
      needsAi: false,
    };
  }

  const mrnMatch = query.match(/\b(?:mrn|chart)\s*[:#]?\s*([a-z0-9-]+)\b/i);
  const dateMatch = query.match(
    /\b(\d{4}-\d{2}-\d{2}|\d{1,2}\/\d{1,2}\/\d{4})\b/
  );

  let chart_number = mrnMatch ? mrnMatch[1].toUpperCase() : "";
  let date_of_birth = "";

  if (dateMatch) {
    const raw = dateMatch[1];
    if (raw.includes("-")) {
      date_of_birth = raw;
    } else {
      const [m, d, y] = raw.split("/");
      date_of_birth = `${y}-${m.padStart(2, "0")}-${d.padStart(2, "0")}`;
    }
  }

  let name = query
    .replace(/\b(?:mrn|chart)\s*[:#]?\s*[a-z0-9-]+\b/gi, "")
    .replace(/\b\d{4}-\d{2}-\d{2}\b/g, "")
    .replace(/\b\d{1,2}\/\d{1,2}\/\d{4}\b/g, "")
    .replace(/\bborn\b/gi, "")
    .trim();

  const needsAi =
    !chart_number &&
    !date_of_birth &&
    /\b(?:born|male|female|patient|mrn)\b/i.test(query);

  return {
    name,
    date_of_birth,
    chart_number,
    needsAi,
  };
}
