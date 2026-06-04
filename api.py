#!/usr/bin/env python3
"""
API Flask — Sistema Integrado de Monitoramento e Backup
Expõe dados reais do sistema via psutil como JSON para o front end.

Uso:
    pip install flask psutil
    python api.py

Acesse:
    http://localhost:5000
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import psutil
import os
import shutil
import zipfile
import tarfile
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

# ─── CONFIGURAÇÃO ────────────────────────────────────────
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s')

app = Flask(__name__, static_folder='.')
CORS(app)  # permite chamadas do front end

BACKUP_DIR = Path('./backups')
LOCAL_PRIMARIO   = BACKUP_DIR / 'local_primario'
LOCAL_SECUNDARIO = BACKUP_DIR / 'local_secundario'
OFFSITE          = BACKUP_DIR / 'offsite'
MANIFESTO_PATH   = BACKUP_DIR / 'manifesto_backups.json'

for d in [LOCAL_PRIMARIO, LOCAL_SECUNDARIO, OFFSITE]:
    d.mkdir(parents=True, exist_ok=True)

# ─── HELPERS ─────────────────────────────────────────────
def load_manifesto():
    if MANIFESTO_PATH.exists():
        with open(MANIFESTO_PATH) as f:
            return json.load(f)
    return {'backups': []}

def save_manifesto(m):
    with open(MANIFESTO_PATH, 'w') as f:
        json.dump(m, f, indent=2)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


# ════════════════════════════════════════════════════════
#  MONITOR — endpoints
# ════════════════════════════════════════════════════════

@app.route('/api/monitor/cpu')
def api_cpu():
    try:
        uso = psutil.cpu_percent(interval=0.2)
        freq = psutil.cpu_freq()
        cores  = psutil.cpu_count(logical=False)
        threads = psutil.cpu_count(logical=True)

        temp = None
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for k in ('coretemp', 'k10temp', 'cpu_thermal'):
                    if k in temps:
                        temp = round(temps[k][0].current, 1)
                        break
                if temp is None:
                    temp = round(list(temps.values())[0][0].current, 1)
        except Exception:
            pass

        return jsonify({
            'uso_percentual':  round(uso, 1),
            'frequencia_atual': round(freq.current, 0) if freq else 0,
            'frequencia_max':   round(freq.max, 0)     if freq else 0,
            'cores':   cores,
            'threads': threads,
            'temperatura': temp
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/ram')
def api_ram():
    try:
        m = psutil.virtual_memory()
        s = psutil.swap_memory()
        return jsonify({
            'total_gb':      round(m.total   / 1e9, 2),
            'usado_gb':      round(m.used    / 1e9, 2),
            'disponivel_gb': round(m.available / 1e9, 2),
            'percentual':    m.percent,
            'swap_total_gb': round(s.total / 1e9, 2),
            'swap_usado_gb': round(s.used  / 1e9, 2),
            'swap_percentual': s.percent
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/disco')
def api_disco():
    try:
        discos = {}
        for p in psutil.disk_partitions():
            try:
                uso = psutil.disk_usage(p.mountpoint)
                discos[p.device] = {
                    'mountpoint':  p.mountpoint,
                    'total_gb':    round(uso.total / 1e9, 2),
                    'usado_gb':    round(uso.used  / 1e9, 2),
                    'livre_gb':    round(uso.free  / 1e9, 2),
                    'percentual':  uso.percent
                }
            except (PermissionError, OSError):
                pass

        io = psutil.disk_io_counters()
        if io:
            discos['io_stats'] = {
                'leitura_mb':  round(io.read_bytes  / 1e6, 1),
                'escrita_mb':  round(io.write_bytes / 1e6, 1),
                'leitura_count': io.read_count,
                'escrita_count': io.write_count
            }
        return jsonify(discos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/rede')
def api_rede():
    try:
        r = psutil.net_io_counters()
        ifaces = psutil.net_if_stats()
        interfaces = {
            name: {
                'status': 'Ativa' if s.isup else 'Inativa',
                'velocidade_mbps': s.speed,
                'mtu': s.mtu
            }
            for name, s in ifaces.items()
        }
        return jsonify({
            'total': {
                'bytes_enviados':   r.bytes_sent,
                'bytes_recebidos':  r.bytes_recv,
                'pacotes_enviados': r.packets_sent,
                'pacotes_recebidos': r.packets_recv,
                'erros_entrada': r.errin,
                'erros_saida':   r.errout
            },
            'interfaces': interfaces
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitor/snapshot')
def api_snapshot():
    """Snapshot completo em uma única chamada (mais eficiente para o front)."""
    try:
        cpu_r = psutil.cpu_percent(interval=0.2)
        freq  = psutil.cpu_freq()
        m     = psutil.virtual_memory()
        s     = psutil.swap_memory()
        io    = psutil.disk_io_counters()
        r     = psutil.net_io_counters()
        ifaces = psutil.net_if_stats()

        temp = None
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for k in ('coretemp', 'k10temp', 'cpu_thermal'):
                    if k in temps:
                        temp = round(temps[k][0].current, 1)
                        break
                if temp is None:
                    temp = round(list(temps.values())[0][0].current, 1)
        except Exception:
            pass

        discos = {}
        for p in psutil.disk_partitions():
            try:
                uso = psutil.disk_usage(p.mountpoint)
                discos[p.device] = {
                    'mountpoint': p.mountpoint,
                    'total_gb':   round(uso.total / 1e9, 2),
                    'usado_gb':   round(uso.used  / 1e9, 2),
                    'livre_gb':   round(uso.free  / 1e9, 2),
                    'percentual': uso.percent
                }
            except (PermissionError, OSError):
                pass

        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'uso_percentual':   round(cpu_r, 1),
                'frequencia_atual': round(freq.current, 0) if freq else 0,
                'frequencia_max':   round(freq.max, 0)     if freq else 0,
                'cores':   psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'temperatura': temp
            },
            'ram': {
                'total_gb':      round(m.total    / 1e9, 2),
                'usado_gb':      round(m.used     / 1e9, 2),
                'disponivel_gb': round(m.available/ 1e9, 2),
                'percentual':    m.percent,
                'swap_total_gb': round(s.total / 1e9, 2),
                'swap_usado_gb': round(s.used  / 1e9, 2),
                'swap_percentual': s.percent
            },
            'disco': {
                'particoes': discos,
                'io': {
                    'leitura_mb':  round(io.read_bytes  / 1e6, 1) if io else 0,
                    'escrita_mb':  round(io.write_bytes / 1e6, 1) if io else 0
                } if io else {}
            },
            'rede': {
                'bytes_enviados':    r.bytes_sent,
                'bytes_recebidos':   r.bytes_recv,
                'pacotes_enviados':  r.packets_sent,
                'pacotes_recebidos': r.packets_recv,
                'interfaces': {
                    name: {
                        'status': 'Ativa' if st.isup else 'Inativa',
                        'velocidade_mbps': st.speed,
                        'mtu': st.mtu
                    }
                    for name, st in ifaces.items()
                }
            }
        })
    except Exception as e:
        logging.exception('Erro no snapshot')
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════════════════════
#  BACKUP — endpoints
# ════════════════════════════════════════════════════════

@app.route('/api/backup/criar', methods=['POST'])
def api_criar_backup():
    data = request.get_json() or {}
    caminho  = data.get('caminho', '').strip()
    formato  = data.get('formato', 'zip').lower()

    if not caminho:
        return jsonify({'ok': False, 'erro': 'Caminho não informado'}), 400
    if not os.path.exists(caminho):
        return jsonify({'ok': False, 'erro': f'Caminho não encontrado: {caminho}'}), 400

    origem = Path(caminho)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')

    try:
        # ── Cria o arquivo de backup ──
        if formato == 'tar':
            nome = f'backup_{origem.name}_{ts}.tar.gz'
            dest = LOCAL_PRIMARIO / nome
            with tarfile.open(dest, 'w:gz') as tar:
                tar.add(origem, arcname=origem.name)
        else:
            nome = f'backup_{origem.name}_{ts}.zip'
            dest = LOCAL_PRIMARIO / nome
            with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zf:
                if origem.is_file():
                    zf.write(origem, origem.name)
                else:
                    for arq in origem.rglob('*'):
                        if arq.is_file():
                            zf.write(arq, arq.relative_to(origem.parent))

        tamanho = dest.stat().st_size
        hash_val = sha256_file(dest)

        # ── Regra 3-2-1 ──
        shutil.copy2(dest, LOCAL_SECUNDARIO / nome)
        shutil.copy2(dest, OFFSITE / nome)

        # ── Manifesto ──
        m = load_manifesto()
        entry = {
            'nome_arquivo': nome,
            'caminho_origem': str(caminho),
            'formato': formato,
            'timestamp': datetime.now().isoformat(),
            'tamanho_bytes': tamanho,
            'hash': hash_val,
            'locais': [str(dest), str(LOCAL_SECUNDARIO/nome), str(OFFSITE/nome)]
        }
        m['backups'].insert(0, entry)
        save_manifesto(m)

        logging.info(f'Backup criado: {nome}')
        return jsonify({
            'ok': True,
            'nome': nome,
            'tamanho_mb': round(tamanho / 1e6, 2),
            'hash': hash_val,
            'locais': entry['locais']
        })

    except Exception as e:
        logging.exception('Erro ao criar backup')
        return jsonify({'ok': False, 'erro': str(e)}), 500


@app.route('/api/backup/listar')
def api_listar_backups():
    m = load_manifesto()
    return jsonify(m['backups'])


@app.route('/api/backup/restaurar', methods=['POST'])
def api_restaurar():
    data = request.get_json() or {}
    nome   = data.get('nome', '').strip()
    destino = data.get('destino', './restaurado').strip() or './restaurado'

    if not nome:
        return jsonify({'ok': False, 'erro': 'Nome do arquivo não informado'}), 400

    arquivo = None
    for local in [LOCAL_PRIMARIO, LOCAL_SECUNDARIO, OFFSITE]:
        c = local / nome
        if c.exists():
            arquivo = c
            break

    if not arquivo:
        return jsonify({'ok': False, 'erro': f'Arquivo "{nome}" não encontrado nos 3 locais'}), 404

    try:
        Path(destino).mkdir(parents=True, exist_ok=True)
        if nome.endswith('.zip'):
            with zipfile.ZipFile(arquivo) as zf:
                zf.extractall(destino)
        else:
            with tarfile.open(arquivo, 'r:*') as tar:
                tar.extractall(destino)

        logging.info(f'Restaurado "{nome}" em "{destino}"')
        return jsonify({'ok': True, 'destino': str(destino)})
    except Exception as e:
        logging.exception('Erro ao restaurar')
        return jsonify({'ok': False, 'erro': str(e)}), 500


@app.route('/api/backup/excluir', methods=['POST'])
def api_excluir():
    data = request.get_json() or {}
    nome = data.get('nome', '').strip()
    if not nome:
        return jsonify({'ok': False, 'erro': 'Nome não informado'}), 400

    m = load_manifesto()
    entry = next((b for b in m['backups'] if b['nome_arquivo'] == nome), None)
    if entry:
        for loc in entry['locais']:
            p = Path(loc)
            if p.exists():
                p.unlink()
        m['backups'] = [b for b in m['backups'] if b['nome_arquivo'] != nome]
        save_manifesto(m)

    return jsonify({'ok': True})


# ── serve o index.html na raiz ───────────────────────────
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')


# ════════════════════════════════════════════════════════
if __name__ == '__main__':
    print()
    print('╔══════════════════════════════════════════╗')
    print('║  SysOps API  —  http://localhost:5000    ║')
    print('╚══════════════════════════════════════════╝')
    print()
    # instala flask-cors se necessário
    try:
        from flask_cors import CORS
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask-cors', '-q'])
        from flask_cors import CORS
    CORS(app)
    app.run(host='0.0.0.0', port=5000, debug=False)
