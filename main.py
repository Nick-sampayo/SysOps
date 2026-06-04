#!/usr/bin/env python3
"""
Sistema Integrado de Monitoramento e Backup
Projeto de Sistemas Operacionais
"""

import sys
import os
import threading
import time
from monitor_sistema import MonitorSistema
from sistema_backup import SistemaBackup

def menu():
    """Exibe o menu principal."""
    print("\n" + "=" * 50)
    print("SISTEMA INTEGRADO - PROJETO SISTEMAS OPERACIONAIS")
    print("=" * 50)
    print("1. Iniciar Monitor de Componentes (CPU, RAM, Disco, Rede)")
    print("2. Realizar Backup Imediato (Regra 3-2-1)")
    print("3. Listar Histórico de Backups")
    print("4. Restaurar um Backup")
    print("5. Sair")
    print("=" * 50)
    return input("Escolha uma opção: ")

def realizar_backup_interativo(backup_system):
    """Interface interativa para realizar backup."""
    caminho = input("\nDigite o caminho do diretório ou arquivo para backup: ")
    if not os.path.exists(caminho):
        print("Erro: Caminho não encontrado!")
        return
    
    print("\nEscolha o formato:")
    print("1. ZIP (Padrão)")
    print("2. TAR.GZ (Linux)")
    formato = input("Opção: ")
    
    print("\nIniciando processo de backup...")
    if formato == '2':
        arquivo_backup = backup_system.criar_backup_tar(caminho)
    else:
        arquivo_backup = backup_system.criar_backup_zip(caminho)
        
    if arquivo_backup:
        sucesso = backup_system.implementar_regra_3_2_1(arquivo_backup)
        if sucesso:
            print("\n[SUCESSO] Backup realizado e replicado (Regra 3-2-1)!")
        else:
            print("\n[ERRO] Falha ao replicar o backup.")
    else:
        print("\n[ERRO] Falha ao criar o arquivo de backup.")

def restaurar_backup_interativo(backup_system):
    """Interface interativa para restaurar backup."""
    backup_system.listar_backups()
    nome_arquivo = input("\nDigite o nome completo do arquivo de backup para restaurar: ")
    destino = input("Digite o diretório de destino (Enter para atual): ") or "."
    
    if backup_system.restaurar_backup(nome_arquivo, destino):
        print(f"\n[SUCESSO] Backup '{nome_arquivo}' restaurado em '{destino}'!")
    else:
        print("\n[ERRO] Falha ao restaurar o backup.")

def main():
    """Função principal."""
    # Inicializa os sistemas
    monitor = MonitorSistema(intervalo=2)
    backup_system = SistemaBackup()
    
    while True:
        opcao = menu()
        
        if opcao == '1':
            try:
                monitor.exibir_monitor_interativo()
            except KeyboardInterrupt:
                pass
        
        elif opcao == '2':
            realizar_backup_interativo(backup_system)
            input("\nPressione Enter para continuar...")
            
        elif opcao == '3':
            backup_system.listar_backups()
            input("\nPressione Enter para continuar...")
            
        elif opcao == '4':
            restaurar_backup_interativo(backup_system)
            input("\nPressione Enter para continuar...")
            
        elif opcao == '5':
            print("\nEncerrando o sistema. Até logo!")
            break
        
        else:
            print("\nOpção inválida! Tente novamente.")
            time.sleep(1)

if __name__ == '__main__':
    main()
