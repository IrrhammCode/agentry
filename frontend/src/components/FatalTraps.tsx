import React, { useState } from 'react';
import { 
  Flame, 
  Repeat, 
  Bomb, 
  EyeOff, 
  CheckCircle, 
  XCircle, 
  ArrowRight,
  TrendingDown,
  DollarSign,
  AlertOctagon,
  Sparkles
} from 'lucide-react';

interface Trap {
  id: string;
  icon: React.ReactNode;
  iconBg: string;
  title: string;
  subtitle: string;
  realWorldStory: string;
  damageCost: string;
  agentryFix: string;
}

const TRAPS: Trap[] = [
  {
    id: 'spiral',
    icon: <Repeat className="w-6 h-6 text-amber-400" />,
    iconBg: 'bg-amber-500/10 border-amber-500/20',
    title: 'The $1,000 Infinite Retry Spiral',
    subtitle: 'Agen AI Mengulang Error 40x Saat Anda Tidur',
    realWorldStory: 'Agen AI Anda gagal menjalankan unit test karena ada koma yang hilang. Alih-alih berhenti, agen terus mengedit baris yang salah dan menjalankan tes yang sama 40 kali berturut-turut. Histori percakapan membengkak hingga 128k token.',
    damageCost: 'Tagihan cloud membengkak $800 - $1,500 dalam satu malam tanpa hasil.',
    agentryFix: 'TabPFN mengenali entropi pengulangan multivariate pada langkah ke-5, memutus loop buntu, dan menghentikan pengeluaran token secara instan.'
  },
  {
    id: 'blast',
    icon: <Bomb className="w-6 h-6 text-sentry-red" />,
    iconBg: 'bg-red-500/10 border-red-500/20',
    title: 'Irreversible Blast Radius',
    subtitle: 'Perintah Terminal Yang Menghapus Seluruh Server',
    realWorldStory: 'Diberikan akses ke terminal bash untuk membersihkan cache, agen berhalusinasi dan menjalankan "rm -rf /" atau menghapus database utama ("DROP TABLE users"). Kerusakan fisik terjadi sebelum manusia sempat menekan tombol cancel.',
    damageCost: 'Data pelanggan hilang permanen, server produksi mati, dan downtime bisnis berhari-hari.',
    agentryFix: 'Agentry Layer 1 mencegat perintah terminal berbahaya dalam <1ms sebelum shell sistem sempat menjalankannya.'
  },
  {
    id: 'leak',
    icon: <EyeOff className="w-6 h-6 text-sentry-violet" />,
    iconBg: 'bg-violet-500/10 border-violet-500/20',
    title: 'Silent Credential Leaks',
    subtitle: 'Kunci Rahasia API & Password Terbocor ke Pihak Luar',
    realWorldStory: 'Banyak sistem pengawas agen mengirim seluruh log percakapan ke LLM komersial pihak ketiga untuk dipantau. Tanpa disadari, file .env, kunci AWS, dan token database Anda ikut terkirim ke server cloud luar.',
    damageCost: 'Kredensial rahasia dicuri, potensi pelanggaran kepatuhan hukum data, dan ancaman penyusupan sistem.',
    agentryFix: '100% Zero-Prompt Transmission: TabPFN hanya membaca 16 metrik angka telemetri. Kode rahasia Anda tidak pernah meninggalkan mesin lokal.'
  }
];

export const FatalTraps: React.FC = () => {
  const [selectedTrap, setSelectedTrap] = useState<string>('spiral');

  return (
    <section id="traps" className="py-20 px-4 lg:px-8 max-w-6xl mx-auto relative">
      
      {/* Header */}
      <div className="text-center mb-14">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-500/10 border border-red-500/30 text-sentry-red text-xs font-mono font-medium mb-3 animate-pulse-glow">
          <Flame className="w-3.5 h-3.5" />
          <span>MENGAPA ATURAN MANUAL SELALU GAGAL?</span>
        </div>
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-display font-bold text-white mb-3">
          3 Jebakan Maut Armada Agen AI Otonom
        </h2>
        <p className="text-slate-300 max-w-2xl mx-auto text-sm sm:text-base leading-relaxed">
          Agen AI bekerja dengan kecepatan tinggi. Tanpa pelindung foundation model yang otonom, kesalahan kecil akan memicu spiral bencana yang sangat mahal.
        </p>
      </div>

      {/* Trap Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {TRAPS.map((trap) => {
          const isSelected = selectedTrap === trap.id;
          return (
            <div 
              key={trap.id}
              onClick={() => setSelectedTrap(trap.id)}
              className={`glass-card rounded-2xl p-6 sm:p-7 border transition-all cursor-pointer flex flex-col justify-between relative overflow-hidden group ${
                isSelected 
                  ? 'bg-surface-2/90 border-white/30 shadow-2xl scale-[1.02]' 
                  : 'hover:bg-surface-2/50 border-white/10 hover:border-white/20'
              }`}
            >
              <div>
                <div className={`w-12 h-12 rounded-xl ${trap.iconBg} border flex items-center justify-center mb-5 group-hover:scale-110 transition-transform`}>
                  {trap.icon}
                </div>

                <div className="text-xs font-mono text-sentry-cyan mb-1">
                  {trap.subtitle}
                </div>

                <h3 className="text-xl font-bold text-white mb-3 group-hover:text-sentry-emerald transition-colors">
                  {trap.title}
                </h3>

                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed mb-6">
                  {trap.realWorldStory}
                </p>
              </div>

              <div className="space-y-3 pt-4 border-t border-white/10 text-xs">
                {/* Damage */}
                <div className="p-3 rounded-xl bg-red-950/30 border border-red-500/25 flex items-start gap-2.5">
                  <XCircle className="w-4 h-4 text-sentry-red shrink-0 mt-0.5" />
                  <span className="text-red-200">
                    <strong className="text-white">Dampak Kerugian:</strong> {trap.damageCost}
                  </span>
                </div>

                {/* Agentry Fix */}
                <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/25 flex items-start gap-2.5">
                  <CheckCircle className="w-4 h-4 text-sentry-emerald shrink-0 mt-0.5" />
                  <span className="text-emerald-200">
                    <strong className="text-white">Solusi Agentry:</strong> {trap.agentryFix}
                  </span>
                </div>
              </div>

              {isSelected && (
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-sentry-cyan via-emerald-400 to-sentry-emerald" />
              )}
            </div>
          );
        })}
      </div>

      {/* Bottom Summary Banner */}
      <div className="mt-10 p-5 rounded-2xl glass-card border border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
        <div className="flex items-center gap-3">
          <Sparkles className="w-5 h-5 text-sentry-emerald animate-pulse" />
          <span className="text-xs sm:text-sm text-slate-200">
            <strong>Kesimpulan:</strong> Agentry bukan sekadar aturan IF/ELSE kaku — Agentry adalah pelindung cerdas berbasis matematika prior Bayesian yang menjaga kode, data, dan anggaran Anda secara otonom.
          </span>
        </div>
        <a 
          href="#playground" 
          className="shrink-0 px-4 py-2 rounded-xl bg-surface-2 hover:bg-surface-3 border border-white/10 text-xs font-mono text-sentry-cyan hover:text-white transition-colors"
        >
          Coba di Simulator ↑
        </a>
      </div>

    </section>
  );
};
