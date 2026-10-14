import { useEffect, useMemo, useState, useRef } from "react"

// ───────────────────────────────── Types ──────────────────────────────
type Leitura = { timestamp: string; temperatura: number; vibracao: number; consumo: number }
type Maquina = { id: number; nome: string; status: string; historico: Leitura[] }

const STORAGE_KEY = "metalsense_mock_v1"

// ───────────────────────── Analytics  (port de analytics.py) ───────────
function _calcEstat(h: Leitura[], metrica: keyof Leitura) {
  if (!h.length) return { min: 0, max: 0, media: 0, desvio: 0, ultima: 0 }
  const vals = h.map((x) => x[metrica] as number).filter((v) => typeof v === "number")
  if (!vals.length) return { min: 0, max: 0, media: 0, desvio: 0, ultima: 0 }
  const media = vals.reduce((a, b) => a + b, 0) / vals.length
  const desvio = vals.length > 1 ? Math.sqrt(vals.reduce((s, v) => s + (v - media) ** 2, 0) / (vals.length - 1)) : 0
  return { min: Math.min(...vals), max: Math.max(...vals), media: +media.toFixed(2), desvio: +desvio.toFixed(2), ultima: vals[vals.length - 1] }
}
void _calcEstat
function calcTendencia(h: Leitura[], metrica: keyof Leitura): string {
  if (h.length < 3) return "Insuficiente"
  const win = h.slice(-5)
  const vals = win.map((x) => x[metrica] as number)
  if (vals.length < 3) return "Estável"
  const n = vals.length
  const xs = vals.map((_, i) => i)
  const mx = xs.reduce((a, b) => a + b, 0) / n
  const my = vals.reduce((a, b) => a + b, 0) / n
  let num = 0, den = 0
  for (let i = 0; i < n; i++) { num += (xs[i] - mx) * (vals[i] - my); den += (xs[i] - mx) ** 2 }
  if (den === 0) return "Estável"
  const slope = num / den
  const lim: Record<string, number> = { temperatura: 0.8, vibracao: 0.3, consumo: 15 }
  const L = lim[metrica] ?? 0.5
  if (slope > L) return "Crescente Acelerada"
  if (slope > L / 3) return "Leve Subida"
  if (slope < -L) return "Queda Acelerada"
  if (slope < -L / 3) return "Leve Descida"
  return "Estável"
}
function healthScore(h: Leitura[]) {
  if (!h.length) return { score: 100, classificacao: "Aguardando Telemetria", cor: "#6B7280", tendencias: { temperatura: "Indefinida", vibracao: "Indefinida", consumo: "Indefinida" } as Record<string, string>, hipoteses: [] as string[], recomendacao: "Inicie o registro de telemetria." }
  const u = h[h.length - 1]
  let s = 100
  if (u.temperatura > 90) s -= 40; else if (u.temperatura > 80) s -= 25; else if (u.temperatura > 72) s -= 10
  if (u.vibracao > 10) s -= 40; else if (u.vibracao > 7) s -= 25; else if (u.vibracao > 5) s -= 10
  if (u.consumo > 550) s -= 30; else if (u.consumo > 450) s -= 15
  const tt = calcTendencia(h, "temperatura"), tv = calcTendencia(h, "vibracao")
  if (tt === "Crescente Acelerada") s -= 8
  if (tv === "Crescente Acelerada") s -= 10
  s = Math.max(0, Math.min(100, Math.round(s * 10) / 10))
  let classificacao = "", cor = "", recomendacao = ""
  if (s >= 85) { classificacao = "Excelente (Operação Segura)"; cor = "#10B981"; recomendacao = "Equipamento em condições nominais. Manter rotina preventiva." }
  else if (s >= 70) { classificacao = "Bom (Operação Normal)"; cor = "#38BDF8"; recomendacao = "Estável com oscilações normais." }
  else if (s >= 50) { classificacao = "Atenção (Degradação Detectada)"; cor = "#F59E0B"; recomendacao = "Acompanhar tendências 12h. Programar inspeção." }
  else { classificacao = "Crítico (Risco Alto)"; cor = "#EF4444"; recomendacao = "INTERVENÇÃO IMEDIATA: risco de dano severo." }
  const hip: string[] = []
  if (u.vibracao > 7 && u.temperatura > 75) hip.push("FALHA MECÂNICA GRAVE: desgaste severo de rolamento ou perda de lubrificação.")
  else if (u.vibracao > 6) hip.push("DESALINHAMENTO / DESBALANCEAMENTO: vibração elevada sugere folga ou desbalanceamento.")
  if (u.consumo > 480 && u.temperatura > 80) hip.push("SOBRECARGA ELÉTRICA / TÉRMICA: risco de queima de enrolamento.")
  else if (u.consumo > 480) hip.push("SOBRECARGA OPERACIONAL: demanda mecânica elevada.")
  if (u.temperatura > 85 && u.vibracao <= 6 && u.consumo <= 480) hip.push("FALHA DE REFRIGERAÇÃO: superaquecimento sem esforço mecânico.")
  return { score: s, classificacao, cor, tendencias: { temperatura: tt, vibracao: tv, consumo: calcTendencia(h, "consumo") }, hipoteses: hip, recomendacao }
}

// ───────────────────────── Simulador  (port de simulador_iot + maquinas) ─
function nowTS() { const d = new Date(); const pad = (n:number)=>String(n).padStart(2,"0"); return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}` }
function simularLeitura(anomalia=false): Leitura {
  const r=(a:number,b:number)=>+(Math.random()*(b-a)+a).toFixed(2)
  if(!anomalia) return { timestamp: nowTS(), temperatura: r(55,68), vibracao: r(2,4.5), consumo: r(250,380)}
  const tipo=["temperatura","vibracao","consumo","multiplo"][Math.floor(Math.random()*4)]
  if(tipo==="temperatura") return {timestamp:nowTS(), temperatura:r(88,115), vibracao:r(2,4.5), consumo:r(250,380)}
  if(tipo==="vibracao") return {timestamp:nowTS(), temperatura:r(55,68), vibracao:r(9.5,18), consumo:r(250,380)}
  if(tipo==="consumo") return {timestamp:nowTS(), temperatura:r(55,68), vibracao:r(2,4.5), consumo:r(550,850)}
  return {timestamp:nowTS(), temperatura:r(85,110), vibracao:r(10,16), consumo:r(500,750)}
}
function cenarioLeitura(cenario:string): Leitura {
  const r=(a:number,b:number)=>+(Math.random()*(b-a)+a).toFixed(2)
  if(cenario==="rolamento") return {timestamp:nowTS(), temperatura:r(62,78), vibracao:r(7.5,14), consumo:r(280,420)}
  if(cenario==="aquecimento") return {timestamp:nowTS(), temperatura:r(88,108), vibracao:r(2.5,5), consumo:r(300,460)}
  if(cenario==="sobrecarga") return {timestamp:nowTS(), temperatura:r(68,82), vibracao:r(3,6), consumo:r(520,780)}
  return simularLeitura()
}
function analisarStatus(h: Leitura[]): string {
  if(h.length<2) return "sem dados"
  const u=h[h.length-1]
  if(u.temperatura>85||u.vibracao>8||u.consumo>500) return "anomalia"
  if(h.length>=3){
    const base=h.slice(0,-1)
    for(const met of ["temperatura","vibracao","consumo"] as const){
      const vals=base.map(v=>v[met]); const m=vals.reduce((a,b)=>a+b,0)/vals.length; const dev=Math.sqrt(vals.reduce((s,v)=>s+(v-m)**2,0)/(vals.length-1||1))
      if(dev>0.05 && Math.abs((u[met] as number)-m) > 2.5*dev) return "anomalia"
    }
  }
  return "normal"
}

// ───────────────────────── Mock inicial ───────────────────────────────
const MOCK_INICIAL: Maquina[] = [
  { id: 1, nome: "Linha de Corte CNC 01", status: "normal", historico: [
    {timestamp:"2026-10-14 09:00:00",temperatura:61.2,vibracao:3.1,consumo:312},{timestamp:"2026-10-14 09:05:00",temperatura:62.4,vibracao:3.4,consumo:328},{timestamp:"2026-10-14 09:10:00",temperatura:60.8,vibracao:2.9,consumo:305},{timestamp:"2026-10-14 09:15:00",temperatura:63.1,vibracao:3.6,consumo:341},
  ]},
  { id: 2, nome: "Prensa Hidráulica 02", status: "anomalia", historico: [
    {timestamp:"2026-10-14 09:00:00",temperatura:68.4,vibracao:5.2,consumo:412},{timestamp:"2026-10-14 09:05:00",temperatura:74.1,vibracao:7.8,consumo:489},{timestamp:"2026-10-14 09:10:00",temperatura:89.3,vibracao:9.4,consumo:612},
  ]},
  { id: 3, nome: "Torno Mecânico 03", status: "normal", historico: [
    {timestamp:"2026-10-14 09:00:00",temperatura:58.9,vibracao:2.4,consumo:278},{timestamp:"2026-10-14 09:05:00",temperatura:59.3,vibracao:2.7,consumo:294},
  ]},
  { id: 4, nome: "Fresadora Industrial 04", status: "sem dados", historico: []},
]

// ───────────────────────── Ícones SVG (traço 1.7) ─────────────────────
const I = {
  panelClose: (c="currentColor",s=15)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/><path d="m16 15-3-3 3-3"/></svg>`,
  panelOpen: (c="currentColor",s=15)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/><path d="m14 9 3 3-3 3"/></svg>`,
  chevronDown: (c="rgba(255,255,255,0.4)",s=14)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>`,
  chevronRight:(c="rgba(255,255,255,0.35)",s=12)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>`,
  search:(c="rgba(255,255,255,0.35)",s=13)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>`,
  grid:(c="rgba(255,255,255,0.55)",s=14)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>`,
  cpu:(c="rgba(255,255,255,0.55)",s=14)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>`,
  activity:(c="rgba(255,255,255,0.55)",s=14)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>`,
  settings:(c="rgba(255,255,255,0.55)",s=14)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>`,
  book:(c="rgba(255,255,255,0.55)",s=14)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>`,
}

// ───────────────────────── Componentes visuais ────────────────────────
function Gauge({ score }: { score: number }) {
  const r = 54, circ = 2 * Math.PI * r, pct = Math.max(0, Math.min(100, score)), off = circ * (1 - pct / 100)
  const color = pct >= 75 ? "#F2F2F3" : pct >= 50 ? "#F59E0B" : "#EF4444"
  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: 140, height: 140 }}>
        <svg width={140} height={140} className="-rotate-90">
          <circle cx={70} cy={70} r={r} fill="none" stroke="#222224" strokeWidth={10} />
          <circle cx={70} cy={70} r={r} fill="none" stroke={color} strokeWidth={10} strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={off} style={{ transition: "stroke-dashoffset .6s ease" }} />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-mono text-[28px] font-bold tracking-tight text-[#F2F2F3]">{pct.toFixed(0)}%</span>
          <span className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#6B7280]">Saúde</span>
        </div>
      </div>
      <div className="mt-2 flex gap-1.5 text-[9px] font-mono">
        <span className="h-1.5 w-8 rounded-full bg-[#EF4444]/30" /><span className="h-1.5 w-8 rounded-full bg-[#F59E0B]/30" /><span className="h-1.5 w-8 rounded-full bg-white/15" />
      </div>
    </div>
  )
}
function Sparkline({ data, color = "#F2F2F3", limite }: { data: number[]; color?: string; limite?: number }) {
  if (!data.length) return <div className="h-[72px] rounded-[10px] bg-[#222224] border border-white/[0.04]" />
  const w = 320, h = 72, pad = 6
  const min = Math.min(...data, limite ?? Infinity) - 2, max = Math.max(...data, limite ?? -Infinity) + 2
  const range = max - min || 1
  const pts = data.map((v, i) => `${pad + (i / Math.max(1, data.length - 1)) * (w - pad * 2)},${h - pad - ((v - min) / range) * (h - pad * 2)}`).join(" ")
  const limY = limite !== undefined ? h - pad - ((limite - min) / range) * (h - pad * 2) : null
  return (
    <div className="rounded-[10px] border border-white/[0.04] bg-[#161618] p-2">
      <svg viewBox={`0 0 ${w} ${h}`} width="100%" height={h} preserveAspectRatio="none">
        {[0, 1, 2].map((i) => <line key={i} x1={0} x2={w} y1={pad + i * (h - pad * 2) / 3} y2={pad + i * (h - pad * 2) / 3} stroke="rgba(255,255,255,0.04)" strokeWidth={0.8} />)}
        {limY !== null && <line x1={0} x2={w} y1={limY} y2={limY} stroke="#6B7280" strokeWidth={0.9} strokeDasharray="3 3" />}
        <polyline fill="none" stroke={color} strokeWidth={1.7} strokeLinejoin="round" strokeLinecap="round" points={pts} />
        {data.map((v, i) => {
          const x = pad + (i / Math.max(1, data.length - 1)) * (w - pad * 2), y = h - pad - ((v - min) / range) * (h - pad * 2)
          return <circle key={i} cx={x} cy={y} r={2.2} fill={color} />
        })}
      </svg>
    </div>
  )
}

// ───────────────────────── App ─────────────────────────────────────
export default function App() {
  const [maquinas, setMaquinas] = useState<Maquina[]>(() => {
    try { const raw = localStorage.getItem(STORAGE_KEY); if (raw) return JSON.parse(raw) as Maquina[] } catch { /* ignore */ }
    return MOCK_INICIAL
  })
  const [ativaId, setAtivaId] = useState<number | null>(null)
  const [busca, setBusca] = useState("")
  const [novaNome, setNovaNome] = useState("")
  const [buscaFocada, setBuscaFocada] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(() => (typeof window !== "undefined" ? window.innerWidth >= 1024 : true))
  const [toast, setToast] = useState<string | null>(null)
  const searchRef = useRef<HTMLInputElement>(null)

  // fecha sidebar mobile ao teclar Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && typeof window !== "undefined" && window.innerWidth < 1024) {
        setSidebarOpen(false)
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  const selecionarVisaoGeral = () => {
    setAtivaId(null)
    if (typeof window !== "undefined" && window.innerWidth < 1024) setSidebarOpen(false)
  }
  const selecionarMaquina = (id: number) => {
    setAtivaId(id)
    if (typeof window !== "undefined" && window.innerWidth < 1024) setSidebarOpen(false)
  }

  // persist
  useEffect(() => { localStorage.setItem(STORAGE_KEY, JSON.stringify(maquinas)) }, [maquinas])
  // fetch do backend se disponível (não bloqueia)
  useEffect(() => {
    fetch("/api/maquinas").then(r=>r.ok?r.json():null).then(j=>{
      if(j?.maquinas?.length){
        // tenta hidratar mantendo histórico local se backend não tiver
        // se backend tiver dados reais, usa
        const mapped: Maquina[] = j.maquinas.map((m:any)=>({ id:m.id, nome:m.nome, status:m.status, historico: m.historico ?? maquinas.find(x=>x.id===m.id)?.historico ?? [] }))
        // só substitui se tiver mais dados
        if(mapped.length) setMaquinas(prev=> mapped.map(mm=> prev.find(p=>p.id===mm.id)?.historico.length ? prev.find(p=>p.id===mm.id)! : mm))
      }
    }).catch(()=>{})
  // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])

  useEffect(()=>{
    const h=(e:KeyboardEvent)=>{ if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==="k"){ e.preventDefault(); searchRef.current?.focus() } }
    window.addEventListener("keydown",h); return ()=>window.removeEventListener("keydown",h)
  },[])
  useEffect(()=>{ if(toast){ const t=setTimeout(()=>setToast(null),2200); return ()=>clearTimeout(t)}},[toast])

  const ativa = useMemo(()=> maquinas.find(m=>m.id===ativaId) ?? null ,[maquinas,ativaId])
  const filtradas = useMemo(()=>{
    const q=busca.trim().toLowerCase()
    if(!q) return maquinas
    return maquinas.filter(m=> m.nome.toLowerCase().includes(q) || String(m.id).includes(q))
  },[maquinas,busca])
  const kpis = useMemo(()=>{
    const total=maquinas.length, anom=maquinas.filter(m=>m.status==="anomalia").length
    const totalLeit=maquinas.reduce((s,m)=>s+m.historico.length,0)
    const scores=maquinas.filter(m=>m.historico.length).map(m=>healthScore(m.historico).score)
    const media= scores.length ? +(scores.reduce((a,b)=>a+b,0)/scores.length).toFixed(1) : 100
    return {total,anom,totalLeit,media}
  },[maquinas])

  const showToast=(msg:string)=>setToast(msg)

  const criarMaquina=()=>{
    const nome=novaNome.trim(); if(!nome) return showToast("Digite um nome válido.")
    const id=Math.max(0,...maquinas.map(m=>m.id))+1
    const nova:Maquina={id,nome,status:"sem dados",historico:[]}
    setMaquinas(v=>[...v,nova]); setAtivaId(id); setNovaNome(""); showToast(`Ativo “${nome}” cadastrado`)
    fetch("/api/maquinas",{method:"POST",headers:{"Content-Type":"application/json","X-API-Key":"dev"},body:JSON.stringify({nome})}).catch(()=>{})
  }
  const removerAtiva=()=>{
    if(!ativa) return
    setMaquinas(v=>v.filter(m=>m.id!==ativa.id)); setAtivaId(null); showToast("Ativo removido")
    fetch(`/api/maquinas/${ativa.id}`,{method:"DELETE",headers:{"X-API-Key":"dev"}}).catch(()=>{})
  }
  const registrar=(id:number, leitura:Leitura)=>{
    setMaquinas(prev=> prev.map(m=>{
      if(m.id!==id) return m
      const novoHist=[...m.historico,leitura]
      return {...m, historico:novoHist, status: analisarStatus(novoHist)}
    }))
  }
  const coletarTodas=()=>{
    setMaquinas(prev=> prev.map(m=>{
      const leit=simularLeitura(false); const h=[...m.historico,leit]; return {...m,historico:h,status:analisarStatus(h)}
    })); showToast("Amostragens coletadas em tempo real")
  }
  const coletarUma=(id:number, anomalia=false)=>{ const l=simularLeitura(anomalia); registrar(id,l); showToast(anomalia?"Falha simulada injetada":"Leitura registrada")}
  const injetarCenario=(id:number, c:string)=>{ const l=cenarioLeitura(c); registrar(id,l); showToast(`Cenário ${c} injetado`)}

  const exportCSV=(m:Maquina)=>{
    const rows=[["timestamp","temperatura","vibracao","consumo"],...m.historico.map(r=>[r.timestamp,String(r.temperatura),String(r.vibracao),String(r.consumo)])]
    const csv=rows.map(r=>r.join(",")).join("\n")
    const blob=new Blob([csv],{type:"text/csv"}); const url=URL.createObjectURL(blob); const a=document.createElement("a"); a.href=url; a.download=`historico_maquina_${m.id}.csv`; a.click(); URL.revokeObjectURL(url)
  }

  // ───────── Render ─────────
  return (
    <div className="min-h-screen bg-black p-2 sm:p-3 lg:p-4">
      {/* Janela flutuante */}
      <div className="mx-auto flex min-h-[calc(100vh-16px)] max-w-[1440px] overflow-hidden rounded-[18px] border border-white/[0.07] bg-[#0E0E10] shadow-[0_10px_30px_rgba(0,0,0,0.45)] sm:min-h-[calc(100vh-24px)] lg:min-h-[calc(100vh-32px)]">
        {/* Sidebar 25-30% */}
        <aside
          className={`fixed inset-y-0 left-0 z-40 flex w-[300px] max-w-[85vw] flex-col border-r border-white/[0.04] bg-[#121214] shadow-2xl transition-transform duration-200 ease-out lg:static lg:max-w-none lg:w-[300px] xl:w-[320px] lg:shadow-none lg:transition-none ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full lg:hidden"
          }`}
        >
          <div className="flex flex-1 flex-col overflow-hidden">
            {/* Cabeçalho */}
            <div className="flex items-center gap-3 px-4 pb-3 pt-4">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[10px] bg-white text-[15px] font-extrabold tracking-[-0.5px] text-black">M</div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-1.5 text-[13px] font-semibold tracking-[-0.2px] text-white">MetalSense <span dangerouslySetInnerHTML={{__html: I.chevronDown()}} className="flex" /></div>
                <div className="truncate text-[11px] leading-none text-white/45">TechForge • Indústria 4.0</div>
              </div>
              <button
                type="button"
                onClick={() => setSidebarOpen(false)}
                className="flex items-center justify-center rounded-lg border border-white/[0.06] bg-white/[0.03] p-1.5 text-white/50 transition hover:bg-white/[0.06] hover:text-white cursor-pointer"
                aria-label="Recolher barra lateral"
                title="Recolher barra lateral"
              >
                <span dangerouslySetInnerHTML={{__html: I.panelClose("rgba(255,255,255,0.6)",14)}} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-3 pb-4">
              {/* NAVEGAÇÃO */}
              <div className="px-2 pb-1.5 pt-3 text-[10px] font-semibold uppercase tracking-[0.14em] text-white/30">Navegação</div>
              <button
                onClick={selecionarVisaoGeral}
                className={`flex w-full items-center justify-between rounded-[12px] border px-3 py-[9px] text-left text-[13px] font-[450] transition ${ativaId===null ? "border-white/15 bg-white/[0.08] font-semibold text-white" : "border-transparent text-white/55 hover:bg-white/[0.04] hover:text-white"}`}
              >
                <span className="flex items-center gap-2.5"><span dangerouslySetInnerHTML={{__html: I.grid(ativaId===null?"#fff":"rgba(255,255,255,0.55)")}} /> Visão Geral da Planta</span>
              </button>

              {/* ATIVOS EM OPERAÇÃO */}
              <div className="px-2 pb-1.5 pt-4 text-[10px] font-semibold uppercase tracking-[0.14em] text-white/30">Ativos em Operação</div>

              {/* Busca dentro da sidebar (filtra lista) */}
              <div className="relative mb-2">
                <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 opacity-40" dangerouslySetInnerHTML={{__html: I.search()}} />
                <input value={busca} onChange={e=>setBusca(e.target.value)} placeholder="Filtrar ativos..." className="h-8 w-full rounded-[10px] border border-white/[0.06] bg-[#1A1A1E] py-1 pl-8 pr-3 text-[13px] text-[#F2F2F3] placeholder:text-white/30 outline-none focus:border-white/15" />
              </div>

              <div className="space-y-0.5">
                {filtradas.length===0 && <div className="px-3 py-2 text-[12px] text-white/30">Nenhum ativo encontrado.</div>}
                {filtradas.map(m=>{
                  const active=ativaId===m.id, alert=m.status==="anomalia"
                  return (
                    <button key={m.id} onClick={()=>selecionarMaquina(m.id)}
                      className={`flex w-full items-center justify-between rounded-[12px] border px-3 py-[9px] text-left text-[13px] transition ${active ? "border-white/15 bg-white/[0.08] font-semibold text-white" : "border-transparent text-white/55 hover:bg-white/[0.04] hover:text-white"}`}>
                      <span className="flex min-w-0 items-center gap-2.5">
                        <span dangerouslySetInnerHTML={{__html: I.cpu(active?"#fff":"rgba(255,255,255,0.5)")}} className="shrink-0" />
                        <span className="truncate">#{String(m.id).padStart(2,"0")} {m.nome}</span>
                      </span>
                      <span className="flex shrink-0 items-center gap-1.5">
                        {alert && <span className="flex h-5 min-w-5 items-center justify-center rounded-full border border-white/10 bg-[#1E1E20] px-1.5 text-[10px] font-bold text-white/70">!</span>}
                        <span dangerouslySetInnerHTML={{__html: I.chevronRight(active?"rgba(255,255,255,0.6)":"rgba(255,255,255,0.30)")}} />
                      </span>
                    </button>
                  )
                })}
              </div>

              {/* GESTÃO DE ATIVOS */}
              <div className="px-2 pb-1.5 pt-5 text-[10px] font-semibold uppercase tracking-[0.14em] text-white/30">Gestão de Ativos</div>
              <div className="space-y-2">
                <input value={novaNome} onChange={e=>setNovaNome(e.target.value)} onKeyDown={e=> e.key==="Enter" && criarMaquina()} placeholder="Nome do novo ativo..." className="h-9 w-full rounded-[10px] border border-white/[0.06] bg-[#1A1A1E] px-3 text-[13px] text-white placeholder:text-white/30 outline-none focus:border-white/15" />
                <button onClick={criarMaquina} className="flex h-9 w-full items-center justify-center rounded-[12px] bg-white text-[13px] font-semibold text-black hover:bg-white/90">+ Cadastrar Ativo</button>
              </div>

              {ativa && (
                <div className="mt-3 rounded-[12px] border border-white/[0.06] bg-white/[0.02] p-3">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-white/50">Ativo selecionado</div>
                  <div className="mt-1 truncate text-[13px] font-semibold text-white">#{String(ativa.id).padStart(2,"0")} {ativa.nome}</div>
                  <button onClick={removerAtiva} className="mt-2 w-full rounded-[10px] border border-red-500/20 bg-red-500/10 py-1.5 text-[12px] font-medium text-red-400 hover:bg-red-500/15">Remover máquina</button>
                </div>
              )}
            </div>

            {/* Rodapé */}
            <div className="border-t border-white/[0.04] px-3 py-3">
              <div className="space-y-0.5">
                <button className="flex w-full items-center gap-2.5 rounded-[12px] border border-transparent px-3 py-2 text-left text-[13px] text-white/55 hover:bg-white/[0.04] hover:text-white">
                  <span dangerouslySetInnerHTML={{__html: I.settings()}} /> Configurações do Sistema
                </button>
                <button className="flex w-full items-center gap-2.5 rounded-[12px] border border-transparent px-3 py-2 text-left text-[13px] text-white/55 hover:bg-white/[0.04] hover:text-white">
                  <span dangerouslySetInnerHTML={{__html: I.book()}} /> Documentação & API
                </button>
              </div>
              <div className="mt-3 flex items-center gap-2.5 rounded-[12px] border border-white/[0.04] bg-white/[0.02] px-3 py-2">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white text-[11px] font-bold text-black">TF</div>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-[12px] font-medium leading-none text-[#F2F2F3]">Operador Confiabilidade</div>
                  <div className="text-[10px] text-[#6B7280]">TechForge Industrial</div>
                </div>
                <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-[#10B981]" />
              </div>
            </div>
          </div>
        </aside>

        {/* Main 70-75% */}
        <main className="flex min-w-0 flex-1 flex-col bg-[#161618] lg:rounded-r-[18px]">
          {/* Header */}
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.07] px-4 py-3 sm:px-6">
            <div className="flex min-w-0 items-center gap-3">
              <button
                type="button"
                onClick={() => setSidebarOpen((v) => !v)}
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-[8px] border border-white/[0.07] bg-white/[0.03] text-white/60 transition hover:bg-white/[0.06] hover:text-white cursor-pointer"
                aria-label="Alternar menu"
                title={sidebarOpen ? "Recolher barra lateral" : "Expandir barra lateral"}
              >
                <span dangerouslySetInnerHTML={{ __html: sidebarOpen ? I.panelClose("rgba(255,255,255,0.6)", 14) : I.panelOpen("rgba(255,255,255,0.6)", 14) }} />
              </button>
              <nav className="flex flex-wrap items-center gap-1.5 text-[13px]">
                <span className="text-white/35">Workspace</span><span className="text-white/20">/</span>
                <span className="text-white/35">MetalSense</span><span className="text-white/20">/</span>
                {ativa ? <span className="font-[550] text-white">#{String(ativa.id).padStart(2,"0")} {ativa.nome}</span> : <span className="font-[550] text-white">Visão Geral da Planta</span>}
              </nav>
              {ativa ? (
                ativa.status==="anomalia"
                  ? <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/20 bg-amber-500/10 px-2.5 py-1 text-[11px] font-medium text-amber-300"><span className="h-1.5 w-1.5 rounded-full bg-amber-400" />Alerta Operacional</span>
                  : <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-300"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />Operação Normal</span>
              ) : <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-300"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />Telemetria Ao Vivo</span>}
            </div>
            <div className="flex items-center gap-2.5">
              <div className={`flex h-9 items-center gap-2 rounded-full border bg-[#1E1E20] px-3.5 text-[13px] transition ${buscaFocada ? "border-white/15" : "border-white/[0.06]"}`}>
                <span dangerouslySetInnerHTML={{__html: I.search()}} className="shrink-0" />
                <input ref={searchRef} value={busca} onChange={e=>setBusca(e.target.value)} onFocus={()=>setBuscaFocada(true)} onBlur={()=>setBuscaFocada(false)} placeholder="Buscar ativos..." className="w-[140px] bg-transparent text-white placeholder:text-white/30 outline-none sm:w-[180px]" />
                <span className="ml-1 hidden rounded-[4px] border border-white/10 bg-white/[0.05] px-1.5 py-0.5 font-mono text-[10px] text-white/40 sm:inline">⌘K</span>
              </div>
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-white/10 bg-white text-[11px] font-bold text-black">TF</div>
            </div>
          </div>

          {/* Conteúdo scrollável */}
          <div className="flex-1 overflow-y-auto px-4 py-5 sm:px-6">
            {/* Topo: bloco retangular horizontal de título */}
            <div className="relative flex flex-wrap items-center justify-between gap-3 overflow-hidden rounded-[14px] border border-white/[0.07] bg-[#1E1E20] px-[18px] py-[14px]">
              <div className="pointer-events-none absolute inset-x-0 top-0 h-[2.5px] bg-white/5"><div className="h-full w-full bg-[#10B981]" /></div>
              <div>
                <div className="text-[14px] font-semibold tracking-[-0.2px] text-[#F2F2F3]">{ativa ? `Ativo #${String(ativa.id).padStart(2,"0")} — ${ativa.nome}` : "Visão Geral da Planta Fabril"}</div>
                <div className="mt-0.5 text-[11px] text-[#9CA3AF]">{ativa ? "Análise Operacional de Linha de Produção" : "Telemetria & Diagnóstico Preditivo em Tempo Real"}</div>
              </div>
              <div className="flex items-center gap-2 font-mono text-[11px] text-[#9CA3AF]">
                <span className="h-1.5 w-1.5 rounded-full bg-[#10B981]" />{ativa ? "Taxa de Ingestão Nominal" : "Gateway IoT • Rate Limiter: 120 req/min"}
              </div>
            </div>

            {/* KPIs em 4 colunas */}
            <div className="mt-4 grid grid-cols-2 gap-0 overflow-hidden rounded-[14px] border border-white/[0.07] bg-[#1E1E20] lg:grid-cols-4">
              {[
                { label: "Ativos Conectados", value: String(kpis.total).padStart(2,"0"), desc: "Linhas industriais ativas" },
                { label: "Saúde Geral da Planta", value: `${kpis.media}%`, desc: "Classificação ponderada" },
                { label: "Alertas Preditivos", value: String(kpis.anom).padStart(2,"0"), desc: kpis.anom>0 ? "Atenção imediata requerida" : "Operação normal" },
                { label: "Medições Ingeridas", value: String(kpis.totalLeit), desc: "Amostragens IoT em tempo real" },
              ].map((k,i)=>(
                <div key={k.label} className={`flex flex-col px-5 py-4 ${i!==3 ? "border-white/[0.04] lg:border-r" : ""} ${i>=2 ? "border-t border-white/[0.04] lg:border-t-0" : ""}`}>
                  <span className="text-[11px] font-semibold uppercase tracking-[0.08em] text-[#9CA3AF]">{k.label}</span>
                  <span className="font-mono text-[22px] font-bold leading-none tracking-tight text-[#F2F2F3] sm:text-[24px]">{k.value}</span>
                  <span className="mt-1 text-[11px] text-[#6B7280]">{k.desc}</span>
                </div>
              ))}
            </div>

            {/* Conteúdo: Visão Geral vs Detalhe */}
            {!ativa ? (
              <>
                {/* Linha intermediária: 2 cards 50/50 */}
                <div className="mt-5 grid gap-4 lg:grid-cols-2">
                  {/* Card esquerdo: Inventário */}
                  <div className="flex flex-col rounded-[14px] border border-white/[0.07] bg-[#1E1E20] p-5 transition hover:border-white/10">
                    <div className="mb-4 flex items-center justify-between border-b border-white/[0.04] pb-3">
                      <span className="text-[13px] font-semibold tracking-[-0.2px] text-[#F2F2F3]">Inventário de Ativos em Operação</span>
                      <span className="rounded-[6px] border border-[#27272A] bg-[#222224] px-2 py-0.5 font-mono text-[10px] font-semibold uppercase text-[#9CA3AF]">{maquinas.length} máquinas</span>
                    </div>
                    {maquinas.length===0 ? (
                      <div className="rounded-[10px] border border-dashed border-white/10 bg-white/[0.02] px-4 py-8 text-center text-[13px] text-white/40">Nenhuma máquina cadastrada. Adicione pela barra lateral.</div>
                    ) : (
                      <div className="space-y-2">
                        {maquinas.map(m=>{
                          const hs=healthScore(m.historico), warn=m.status==="anomalia"
                          return (
                            <div key={m.id} className="flex items-center justify-between rounded-[10px] border border-white/[0.04] bg-[#222224] px-3 py-2.5">
                              <button onClick={()=>setAtivaId(m.id)} className="truncate text-left text-[13px] font-medium text-white hover:underline">#{String(m.id).padStart(2,"0")} {m.nome}</button>
                              <span className="flex items-center gap-2">
                                <span className="font-mono text-[13px] text-white">{hs.score}%</span>
                                <span className={`h-1.5 w-1.5 rounded-full ${warn?"bg-[#EF4444]":"bg-[#10B981]"}`} />
                              </span>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                  {/* Card direito: Diagnóstico */}
                  <div className="flex flex-col rounded-[14px] border border-white/[0.07] bg-[#1E1E20] p-5">
                    <div className="mb-4 flex items-center justify-between border-b border-white/[0.04] pb-3">
                      <span className="text-[13px] font-semibold tracking-[-0.2px] text-[#F2F2F3]">Diagnóstico Preditivo Global</span>
                      <span className="rounded-[6px] border border-[#27272A] bg-[#222224] px-2 py-0.5 font-mono text-[10px] font-semibold uppercase text-[#9CA3AF]">TechForge AI Engine</span>
                    </div>
                    <p className="text-[13px] leading-[1.6] text-[#9CA3AF]">O motor preditivo MetalSense processa variações contínuas de gradiente térmico (dT/dt), picos de aceleração mecânica e flutuações de potência para prevenir paradas críticas não planejadas.</p>
                    <div className="mt-4 rounded-[10px] border border-white/[0.04] bg-[#222224] p-3">
                      <div className="text-[10px] font-bold uppercase tracking-[0.06em] text-[#6B7280]">Pipeline de Ingestão</div>
                      <div className="mt-1 font-mono text-[12px] text-[#F2F2F3]">Gateway IoT • Rate Limiter: 120 req/min • Auth: X-API-Key • SQLite WAL</div>
                    </div>
                    <button onClick={coletarTodas} className="mt-4 w-full rounded-[10px] border border-[#27272A] bg-[#222224] py-2.5 text-[13px] font-medium text-white hover:bg-[#2A2A2E]">Coletar Amostragem em Todas as Máquinas</button>
                  </div>
                </div>

                {/* Base: 4 barras empilhadas */}
                <div className="mt-5 rounded-[14px] border border-white/[0.07] bg-[#1E1E20] p-5">
                  <div className="mb-3.5 flex flex-wrap items-center justify-between gap-2">
                    <span className="inline-flex items-center gap-1.5 rounded-[6px] border border-white/[0.04] bg-white/[0.04] px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.06em] text-[#9CA3AF]">Fluxo de Telemetria Industrial Recente</span>
                    <span className="font-mono text-[11px] text-[#6B7280]">Buffer: {maquinas.reduce((s,m)=>s+m.historico.length,0)} eventos</span>
                  </div>
                  <div className="space-y-2">
                    {(() => {
                      const todas = maquinas.flatMap(m=> m.historico.map(r=> ({...r, maquina_nome:m.nome})) ).sort((a,b)=> (b.timestamp as string).localeCompare(a.timestamp as string))
                      const itens = [...todas.slice(0,4)]
                      while(itens.length<4) itens.push({ maquina_nome:`Linha Operacional ${String(itens.length+1).padStart(2,"0")} — Standby`, timestamp:"Ciclo programado em espera", temperatura:52, vibracao:1.9, consumo:265} as any)
                      return itens.map((it,idx)=>{
                        const anom = (it.temperatura??0)>85 || (it.vibracao??0)>8 || (it.consumo??0)>500
                        return (
                          <div key={idx} className="flex flex-wrap items-center justify-between gap-3 rounded-[10px] border border-white/[0.04] bg-[#222224] px-4 py-3 transition hover:border-white/10 hover:bg-[#2A2A2E]">
                            <span className="flex items-center gap-3">
                              <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${anom?"bg-[#EF4444]":"bg-[#10B981]"}`} />
                              <span className="text-[13px] font-semibold text-white">{it.maquina_nome}</span>
                              <span className="hidden font-mono text-[11px] text-[#6B7280] sm:inline">{it.timestamp}</span>
                            </span>
                            <span className="flex gap-3 font-mono text-[12px] text-[#9CA3AF] sm:gap-4">
                              <span>Temp: <strong className="text-white">{Number(it.temperatura).toFixed(1)}°C</strong></span>
                              <span>Vib: <strong className="text-white">{Number(it.vibracao).toFixed(2)} mm/s</strong></span>
                              <span>Pot: <strong className="text-white">{Number(it.consumo).toFixed(0)} W</strong></span>
                            </span>
                          </div>
                        )
                      })
                    })()}
                  </div>
                </div>
              </>
            ) : (
              <>
                <button onClick={()=>setAtivaId(null)} className="mt-1 rounded-[10px] border border-white/10 bg-[#1E1E20] px-3 py-1.5 text-[12px] font-medium text-white hover:bg-white/10">← Voltar para Visão Geral</button>

                {/* 2 cards 50/50 detalhe */}
                <div className="mt-4 grid gap-4 lg:grid-cols-2">
                  <div className="rounded-[14px] border border-white/[0.07] bg-[#1E1E20] p-5">
                    <div className="mb-4 flex items-center justify-between border-b border-white/[0.04] pb-3">
                      <span className="text-[13px] font-semibold text-white">Saúde Operacional & Diagnóstico</span>
                      <span className="rounded-[6px] border border-[#27272A] bg-[#222224] px-2 py-0.5 font-mono text-[10px] font-semibold uppercase text-[#9CA3AF]">Ativo #{String(ativa.id).padStart(2,"0")}</span>
                    </div>
                    {(() => { const hs=healthScore(ativa.historico); return (
                      <>
                        <div className="flex justify-center py-2"><Gauge score={hs.score} /></div>
                        <div className="mt-2 text-center text-[12px] font-semibold" style={{color:hs.cor}}>{hs.classificacao}</div>
                        <div className="mt-3 rounded-[10px] border border-white/[0.04] bg-[#222224] p-3 text-[13px] leading-[1.55] text-white">{hs.recomendacao}</div>
                        {hs.hipoteses.length>0 && <div className="mt-3 space-y-1">{hs.hipoteses.map((h,i)=><div key={i} className="rounded-[8px] border border-amber-500/20 bg-amber-500/10 px-3 py-2 text-[12px] text-amber-200">{h}</div>)}</div>}
                        <div className="mt-3 flex gap-4 border-t border-white/[0.04] pt-3 font-mono text-[11px] text-[#6B7280]">
                          <span>Temp: <strong className="text-white">{hs.tendencias.temperatura}</strong></span>
                          <span>Vib: <strong className="text-white">{hs.tendencias.vibracao}</strong></span>
                          <span>Pot: <strong className="text-white">{hs.tendencias.consumo}</strong></span>
                        </div>
                      </>
                    )})()}
                  </div>

                  <div className="rounded-[14px] border border-white/[0.07] bg-[#1E1E20] p-5">
                    <div className="mb-4 flex items-center justify-between border-b border-white/[0.04] pb-3">
                      <span className="text-[13px] font-semibold text-white">Telemetria & Injeção de Cenários</span>
                      <span className="rounded-[6px] border border-[#27272A] bg-[#222224] px-2 py-0.5 font-mono text-[10px] font-semibold uppercase text-[#9CA3AF]">{ativa.historico.length} amostras</span>
                    </div>
                    {ativa.historico.length ? (
                      <div className="grid grid-cols-3 gap-2">
                        {[
                          {k:"Temperatura", v: `${ativa.historico[ativa.historico.length-1].temperatura.toFixed(1)}°C`},
                          {k:"Vibração", v: `${ativa.historico[ativa.historico.length-1].vibracao.toFixed(2)} mm/s`},
                          {k:"Consumo", v: `${ativa.historico[ativa.historico.length-1].consumo.toFixed(0)} W`},
                        ].map(x=>(
                          <div key={x.k} className="rounded-[10px] border border-white/[0.04] bg-[#222224] px-2 py-3 text-center">
                            <div className="text-[10px] font-bold uppercase tracking-[0.06em] text-[#6B7280]">{x.k}</div>
                            <div className="mt-1 font-mono text-[15px] font-bold text-white">{x.v}</div>
                          </div>
                        ))}
                      </div>
                    ) : <div className="rounded-[10px] border border-dashed border-white/10 bg-white/[0.02] py-6 text-center text-[12px] text-white/40">Sem leituras ainda.</div>}
                    <div className="mt-4 grid grid-cols-2 gap-2">
                      <button onClick={()=>coletarUma(ativa.id,false)} className="rounded-[10px] border border-white/10 bg-[#222224] py-2.5 text-[13px] font-medium text-white hover:bg-[#2A2A2E]">+ Leitura Normal</button>
                      <button onClick={()=>coletarUma(ativa.id,true)} className="rounded-[10px] bg-white py-2.5 text-[13px] font-semibold text-black hover:bg-white/90">Simular Falha Genérica</button>
                    </div>
                    <div className="mt-3 rounded-[10px] border border-white/[0.04] bg-[#161618] p-3">
                      <div className="mb-2 text-[10px] font-bold uppercase tracking-wide text-white/40">Injetar Cenários Específicos</div>
                      <div className="grid grid-cols-3 gap-2">
                        <button onClick={()=>injetarCenario(ativa.id,"rolamento")} className="rounded-[8px] border border-white/10 bg-[#1E1E20] py-2 text-[12px] font-medium text-white hover:bg-white/10">Rolamento</button>
                        <button onClick={()=>injetarCenario(ativa.id,"aquecimento")} className="rounded-[8px] border border-white/10 bg-[#1E1E20] py-2 text-[12px] font-medium text-white hover:bg-white/10">Aquecimento</button>
                        <button onClick={()=>injetarCenario(ativa.id,"sobrecarga")} className="rounded-[8px] border border-white/10 bg-[#1E1E20] py-2 text-[12px] font-medium text-white hover:bg-white/10">Sobrecarga</button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Base: 4 barras do ativo */}
                <div className="mt-5 rounded-[14px] border border-white/[0.07] bg-[#1E1E20] p-5">
                  <div className="mb-3.5 flex items-center justify-between">
                    <span className="inline-flex items-center gap-1.5 rounded-[6px] border border-white/[0.04] bg-white/[0.04] px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.06em] text-[#9CA3AF]">Últimas 4 Amostragens de Linha</span>
                    <span className="font-mono text-[11px] text-[#6B7280]">Ativo #{String(ativa.id).padStart(2,"0")}</span>
                  </div>
                  <div className="space-y-2">
                    {(() => {
                      const amostras=[...ativa.historico].slice(-4).reverse()
                      while(amostras.length<4) amostras.push({timestamp:"Standby — Amostragem programada", temperatura:55, vibracao:2, consumo:275} as Leitura)
                      return amostras.map((it,idx)=>{
                        const anom=(it.temperatura??0)>85||(it.vibracao??0)>8||(it.consumo??0)>500
                        return (
                          <div key={idx} className="flex flex-wrap items-center justify-between gap-3 rounded-[10px] border border-white/[0.04] bg-[#222224] px-4 py-3">
                            <span className="flex items-center gap-3">
                              <span className={`h-1.5 w-1.5 rounded-full ${anom?"bg-[#EF4444]":"bg-[#10B981]"}`} />
                              <span className="text-[13px] font-semibold text-white">{ativa.nome}</span>
                              <span className="hidden font-mono text-[11px] text-[#6B7280] sm:inline">{it.timestamp}</span>
                            </span>
                            <span className="flex gap-3 font-mono text-[12px] text-[#9CA3AF] sm:gap-4">
                              <span>Temp: <strong className="text-white">{Number(it.temperatura).toFixed(1)}°C</strong></span>
                              <span>Vib: <strong className="text-white">{Number(it.vibracao).toFixed(2)} mm/s</strong></span>
                              <span>Pot: <strong className="text-white">{Number(it.consumo).toFixed(0)} W</strong></span>
                            </span>
                          </div>
                        )
                      })
                    })()}
                  </div>
                </div>

                {/* Gráficos + export */}
                {ativa.historico.length>=2 && (
                  <div className="mt-5 rounded-[14px] border border-white/[0.07] bg-[#1E1E20] p-5">
                    <div className="mb-3 flex items-center justify-between">
                      <span className="text-[13px] font-semibold text-white">Séries de Telemetria</span>
                      <span className="font-mono text-[10px] uppercase tracking-wide text-[#6B7280]">Limites: 85°C / 8 mm/s / 500 W</span>
                    </div>
                    <div className="grid gap-4 md:grid-cols-3">
                      <div><div className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-[#9CA3AF]">Temperatura (°C)</div><Sparkline data={ativa.historico.map(h=>h.temperatura)} color="#F2F2F3" limite={85} /></div>
                      <div><div className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-[#9CA3AF]">Vibração (mm/s)</div><Sparkline data={ativa.historico.map(h=>h.vibracao)} color="#9CA3AF" limite={8} /></div>
                      <div><div className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-[#9CA3AF]">Consumo (W)</div><Sparkline data={ativa.historico.map(h=>h.consumo)} color="#6B7280" limite={500} /></div>
                    </div>
                  </div>
                )}

                <div className="mt-4 flex flex-wrap gap-2">
                  <button onClick={()=>exportCSV(ativa)} className="rounded-[10px] border border-white/10 bg-[#1E1E20] px-4 py-2 text-[13px] font-medium text-white hover:bg-[#2A2A2E]">Baixar Histórico (CSV)</button>
                  <button onClick={()=>showToast("Laudo HTML disponível via API /api/relatorios/…")} className="rounded-[10px] bg-white px-4 py-2 text-[13px] font-semibold text-black hover:bg-white/90">Laudo Técnico (HTML)</button>
                </div>
              </>
            )}

            <div className="h-6" />
          </div>
        </main>
      </div>

      {/* Toast */}
      {toast && <div className="fixed bottom-4 left-1/2 z-50 -translate-x-1/2 rounded-full border border-white/10 bg-[#1E1E20] px-4 py-2 text-[13px] font-medium text-white shadow-xl">{toast}</div>}

      {/* Overlay mobile quando sidebar aberta */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden cursor-pointer"
          aria-hidden="true"
        />
      )}
    </div>
  )
}
