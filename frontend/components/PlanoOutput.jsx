export default function PlanoOutput({ data }) {
  return (
    <div className="bg-gray-50 p-6 rounded-lg shadow-md mt-6 space-y-4">
      <h2 className="text-xl font-semibold mb-2">📘 Plano de Aula Gerado</h2>

      <section>
        <h3 className="font-bold text-blue-700">🎯 Habilidades BNCC</h3>
        <ul className="list-disc ml-6">
          {data.habilidades_bncc?.map((h, i) => (
            <li key={i}>{h}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="font-bold text-blue-700">🧩 Objetivos da Aula</h3>
        <ul className="list-disc ml-6">
          {data.objetivos_aula?.map((o, i) => (
            <li key={i}>{o}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="font-bold text-blue-700">🧠 Metodologia</h3>
        <p>{data.metodologia?.justificativa}</p>
        <ul className="list-disc ml-6">
          {data.metodologia?.metodologias_sugeridas?.map((m, i) => (
            <li key={i}>{m}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="font-bold text-blue-700">🧰 Materiais Necessários</h3>
        <ul className="list-disc ml-6">
          {data.materiais_necessarios?.map((m, i) => (
            <li key={i}>{m}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="font-bold text-blue-700">⏱️ Estrutura da Aula</h3>
        <p>
          <b>Tempo total:</b> {data.estrutura_aula?.tempo_total}
        </p>
        <ul className="list-disc ml-6">
          {data.estrutura_aula?.etapas?.map((e, i) => (
            <li key={i}>
              <b>{e.nome}</b> ({e.tempo}): {e.atividades.join(", ")}
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="font-bold text-blue-700">📏 Avaliação</h3>
        <p>
          <b>Tipos:</b> {data.avaliacao?.tipos?.join(", ")}
        </p>
        <p>
          <b>Critérios:</b> {data.avaliacao?.criterios?.join(", ")}
        </p>
      </section>

      <section>
        <h3 className="font-bold text-blue-700">💡 Para Saber Mais</h3>
        <ul className="list-disc ml-6">
          {data.para_saber_mais?.map((p, i) => (
            <li key={i}>{p}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
