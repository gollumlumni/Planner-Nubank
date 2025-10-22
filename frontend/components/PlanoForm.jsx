"use client";

import { useState } from "react";
import { gerarPlano } from "@/lib/api";
import PlanoOutput from "./PlanoOutput";

export default function PlanoForm() {
  const [form, setForm] = useState({
    tema_conteudo: "",
    publico: "",
    tempo_aula: "",
    objetivos: "",
    recursos_didaticos: "",
  });
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setResultado(null);
    try {
      const res = await gerarPlano(form);
      setResultado(res);
    } catch (err) {
      console.error(err);
      alert("Erro ao gerar plano.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold text-center">
        🧠 Planejador Educacional com IA
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {[
          "tema_conteudo",
          "publico",
          "tempo_aula",
          "objetivos",
          "recursos_didaticos",
        ].map((key) => (
          <input
            key={key}
            type="text"
            placeholder={key.replace("_", " ")}
            value={form[key]}
            onChange={(e) => setForm({ ...form, [key]: e.target.value })}
            className="w-full border p-2 rounded-lg"
            required={["tema_conteudo", "publico", "tempo_aula"].includes(key)}
          />
        ))}
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg w-full"
        >
          {loading ? "Gerando plano..." : "Gerar com IA"}
        </button>
      </form>

      {resultado && <PlanoOutput data={resultado} />}
    </div>
  );
}
