#!/usr/bin/env python3
"""
Sistema de Monitoramento de Componentes do PC
Monitora CPU, RAM, Disco e Rede em tempo real
Similar ao MSI Afterburner
"""

import psutil
import time
import os
from datetime import datetime
from collections import deque
import json

class MonitorSistema:
    def __init__(self, intervalo=1, historico_max=60):
        """
        Inicializa o monitor do sistema.
        
        Args:
            intervalo: Tempo em segundos entre atualizações
            historico_max: Número máximo de registros a manter no histórico
        """
        self.intervalo = intervalo
        self.historico_max = historico_max
        self.historico_cpu = deque(maxlen=historico_max)
        self.historico_ram = deque(maxlen=historico_max)
        self.historico_disco = deque(maxlen=historico_max)
        self.historico_rede = deque(maxlen=historico_max)
        
    def obter_info_cpu(self):
        """Obtém informações de uso da CPU."""
        try:
            uso_cpu = psutil.cpu_percent(interval=0.1)
            freq_cpu = psutil.cpu_freq()
            cores = psutil.cpu_count(logical=False)
            threads = psutil.cpu_count(logical=True)
            
            return {
                'uso_percentual': uso_cpu,
                'frequencia_atual': round(freq_cpu.current, 2) if freq_cpu else 0,
                'frequencia_max': round(freq_cpu.max, 2) if freq_cpu else 0,
                'cores': cores,
                'threads': threads,
                'temperatura': self._obter_temperatura_cpu()
            }
        except Exception as e:
            print(f"Erro ao obter informações de CPU: {e}")
            return None
    
    def obter_info_ram(self):
        """Obtém informações de uso da memória RAM."""
        try:
            memoria = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total_gb': round(memoria.total / (1024**3), 2),
                'usado_gb': round(memoria.used / (1024**3), 2),
                'disponivel_gb': round(memoria.available / (1024**3), 2),
                'percentual': memoria.percent,
                'swap_total_gb': round(swap.total / (1024**3), 2),
                'swap_usado_gb': round(swap.used / (1024**3), 2),
                'swap_percentual': swap.percent
            }
        except Exception as e:
            print(f"Erro ao obter informações de RAM: {e}")
            return None
    
    def obter_info_disco(self):
        """Obtém informações de uso do disco."""
        try:
            discos = {}
            for particao in psutil.disk_partitions():
                try:
                    uso = psutil.disk_usage(particao.mountpoint)
                    discos[particao.device] = {
                        'mountpoint': particao.mountpoint,
                        'total_gb': round(uso.total / (1024**3), 2),
                        'usado_gb': round(uso.used / (1024**3), 2),
                        'livre_gb': round(uso.free / (1024**3), 2),
                        'percentual': uso.percent
                    }
                except PermissionError:
                    pass
            
            # Informações de I/O de disco
            io_disco = psutil.disk_io_counters()
            if io_disco:
                discos['io_stats'] = {
                    'leitura_mb': round(io_disco.read_bytes / (1024**2), 2),
                    'escrita_mb': round(io_disco.write_bytes / (1024**2), 2),
                    'leitura_count': io_disco.read_count,
                    'escrita_count': io_disco.write_count
                }
            
            return discos
        except Exception as e:
            print(f"Erro ao obter informações de disco: {e}")
            return None
    
    def obter_info_rede(self):
        """Obtém informações de uso da rede."""
        try:
            rede = psutil.net_io_counters()
            interfaces = psutil.net_if_stats()
            
            info_rede = {
                'total': {
                    'bytes_enviados': rede.bytes_sent,
                    'bytes_recebidos': rede.bytes_recv,
                    'pacotes_enviados': rede.packets_sent,
                    'pacotes_recebidos': rede.packets_recv,
                    'erros_entrada': rede.errin,
                    'erros_saida': rede.errout
                },
                'interfaces': {}
            }
            
            for interface, stats in interfaces.items():
                info_rede['interfaces'][interface] = {
                    'status': 'Ativa' if stats.isup else 'Inativa',
                    'velocidade_mbps': stats.speed,
                    'mtu': stats.mtu
                }
            
            return info_rede
        except Exception as e:
            print(f"Erro ao obter informações de rede: {e}")
            return None
    
    def _obter_temperatura_cpu(self):
        """Obtém a temperatura da CPU se disponível."""
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return round(temps['coretemp'][0].current, 2)
            elif temps:
                primeira_chave = list(temps.keys())[0]
                return round(temps[primeira_chave][0].current, 2)
        except:
            pass
        return None
    
    def obter_snapshot(self):
        """Obtém um snapshot completo do estado do sistema."""
        timestamp = datetime.now().isoformat()
        
        snapshot = {
            'timestamp': timestamp,
            'cpu': self.obter_info_cpu(),
            'ram': self.obter_info_ram(),
            'disco': self.obter_info_disco(),
            'rede': self.obter_info_rede()
        }
        
        # Adiciona ao histórico
        if snapshot['cpu']:
            self.historico_cpu.append(snapshot['cpu']['uso_percentual'])
        if snapshot['ram']:
            self.historico_ram.append(snapshot['ram']['percentual'])
        if snapshot['disco']:
            # Toma o primeiro disco como referência
            primeiro_disco = list(snapshot['disco'].keys())[0]
            if primeiro_disco != 'io_stats':
                self.historico_disco.append(snapshot['disco'][primeiro_disco]['percentual'])
        
        return snapshot
    
    def exibir_monitor_interativo(self):
        """Exibe um monitor interativo no terminal."""
        try:
            while True:
                # Limpa a tela de forma mais robusta
                if os.name == 'nt':  # Windows
                    os.system('cls')
                else:  # Linux / Mac
                    print("\033[H\033[J", end="") # Sequência ANSI para limpar tela
                    os.system('clear')
                
                snapshot = self.obter_snapshot()
                
                print("=" * 80)
                print("MONITOR DE SISTEMA - COMPONENTES DO PC")
                print("=" * 80)
                print(f"Horário: {snapshot['timestamp']}\n")
                
                # CPU
                if snapshot['cpu']:
                    cpu = snapshot['cpu']
                    print(f"CPU - Uso: {cpu['uso_percentual']:.1f}%")
                    print(f"  Frequência: {cpu['frequencia_atual']} MHz / {cpu['frequencia_max']} MHz")
                    print(f"  Cores: {cpu['cores']} | Threads: {cpu['threads']}")
                    if cpu['temperatura']:
                        print(f"  Temperatura: {cpu['temperatura']}°C")
                    print()
                
                # RAM
                if snapshot['ram']:
                    ram = snapshot['ram']
                    print(f"MEMÓRIA RAM - Uso: {ram['percentual']:.1f}%")
                    print(f"  {ram['usado_gb']} GB / {ram['total_gb']} GB ({ram['disponivel_gb']} GB disponível)")
                    print(f"  Swap: {ram['swap_usado_gb']} GB / {ram['swap_total_gb']} GB ({ram['swap_percentual']:.1f}%)")
                    print()
                
                # DISCO
                if snapshot['disco']:
                    print("DISCO")
                    for dispositivo, info in snapshot['disco'].items():
                        if dispositivo != 'io_stats':
                            print(f"  {dispositivo} ({info['mountpoint']})")
                            print(f"    Uso: {info['percentual']:.1f}% - {info['usado_gb']} GB / {info['total_gb']} GB")
                    if 'io_stats' in snapshot['disco']:
                        io = snapshot['disco']['io_stats']
                        print(f"  I/O - Leitura: {io['leitura_mb']} MB | Escrita: {io['escrita_mb']} MB")
                    print()
                
                # REDE
                if snapshot['rede']:
                    rede = snapshot['rede']
                    total = rede['total']
                    print("REDE")
                    print(f"  Dados Enviados: {round(total['bytes_enviados'] / (1024**3), 2)} GB")
                    print(f"  Dados Recebidos: {round(total['bytes_recebidos'] / (1024**3), 2)} GB")
                    print(f"  Pacotes Enviados: {total['pacotes_enviados']}")
                    print(f"  Pacotes Recebidos: {total['pacotes_recebidos']}")
                    print()
                
                print("=" * 80)
                print("Pressione Ctrl+C para sair...")
                print("=" * 80)
                
                time.sleep(self.intervalo)
                
        except KeyboardInterrupt:
            print("\n\nMonitor encerrado pelo usuário.")
    
    def salvar_historico_json(self, arquivo='historico_sistema.json'):
        """Salva o histórico em um arquivo JSON."""
        historico = {
            'cpu': list(self.historico_cpu),
            'ram': list(self.historico_ram),
            'disco': list(self.historico_disco),
            'rede': list(self.historico_rede)
        }
        
        with open(arquivo, 'w') as f:
            json.dump(historico, f, indent=2)
        
        print(f"Histórico salvo em: {arquivo}")


def main():
    """Função principal."""
    print("Iniciando Monitor de Sistema...")
    monitor = MonitorSistema(intervalo=2)
    monitor.exibir_monitor_interativo()


if __name__ == '__main__':
    main()
