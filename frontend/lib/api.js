export async function gerarPlano(data) {
  const res = await fetch("http://localhost:8000/gerar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) throw new Error("Erro ao gerar plano");
  return await res.json();
}
