#!/usr/bin/env python3
"""
Sistema de Backup Automatizado
Implementa a estratégia de backup 3-2-1:
- 3 cópias dos dados
- Em 2 mídias diferentes
- 1 cópia fora do local (offsite)
"""

import os
import shutil
import json
import zipfile
import tarfile
from datetime import datetime
from pathlib import Path
import logging
import hashlib

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_sistema.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SistemaBackup:
    def __init__(self, diretorio_base='./backups'):
        """
        Inicializa o sistema de backup.
        
        Args:
            diretorio_base: Diretório base para armazenar backups
        """
        self.diretorio_base = Path(diretorio_base)
        self.diretorio_base.mkdir(exist_ok=True)
        
        # Cria estrutura de diretórios para a regra 3-2-1
        self.local_primario = self.diretorio_base / 'local_primario'
        self.local_secundario = self.diretorio_base / 'local_secundario'
        self.offsite = self.diretorio_base / 'offsite'
        
        for diretorio in [self.local_primario, self.local_secundario, self.offsite]:
            diretorio.mkdir(exist_ok=True)
        
        self.arquivo_manifesto = self.diretorio_base / 'manifesto_backups.json'
        self.carregar_manifesto()
        
        logger.info("Sistema de Backup inicializado")
    
    def carregar_manifesto(self):
        """Carrega o manifesto de backups existentes."""
        if self.arquivo_manifesto.exists():
            with open(self.arquivo_manifesto, 'r') as f:
                self.manifesto = json.load(f)
        else:
            self.manifesto = {'backups': []}
    
    def salvar_manifesto(self):
        """Salva o manifesto de backups."""
        with open(self.arquivo_manifesto, 'w') as f:
            json.dump(self.manifesto, f, indent=2)
    
    def calcular_hash_arquivo(self, caminho_arquivo):
        """Calcula o hash SHA256 de um arquivo."""
        sha256_hash = hashlib.sha256()
        with open(caminho_arquivo, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def calcular_hash_diretorio(self, caminho_diretorio):
        """Calcula o hash de um diretório."""
        sha256_hash = hashlib.sha256()
        for arquivo in sorted(Path(caminho_diretorio).rglob('*')):
            if arquivo.is_file():
                sha256_hash.update(self.calcular_hash_arquivo(arquivo).encode())
        return sha256_hash.hexdigest()
    
    def criar_backup_zip(self, caminho_origem, nome_backup=None):
        """
        Cria um backup em formato ZIP.
        
        Args:
            caminho_origem: Caminho do diretório/arquivo a fazer backup
            nome_backup: Nome do arquivo de backup (opcional)
        
        Returns:
            Caminho do arquivo de backup criado
        """
        caminho_origem = Path(caminho_origem)
        
        if not caminho_origem.exists():
            logger.error(f"Caminho não existe: {caminho_origem}")
            return None
        
        if nome_backup is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_backup = f"backup_{caminho_origem.name}_{timestamp}.zip"
        
        arquivo_backup = self.local_primario / nome_backup
        
        try:
            with zipfile.ZipFile(arquivo_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if caminho_origem.is_file():
                    zipf.write(caminho_origem, arcname=caminho_origem.name)
                else:
                    for arquivo in caminho_origem.rglob('*'):
                        if arquivo.is_file():
                            arcname = arquivo.relative_to(caminho_origem.parent)
                            zipf.write(arquivo, arcname=arcname)
            
            logger.info(f"Backup ZIP criado: {arquivo_backup}")
            return arquivo_backup
        
        except Exception as e:
            logger.error(f"Erro ao criar backup ZIP: {e}")
            return None
    
    def criar_backup_tar(self, caminho_origem, nome_backup=None, compressao='gz'):
        """
        Cria um backup em formato TAR.
        
        Args:
            caminho_origem: Caminho do diretório/arquivo a fazer backup
            nome_backup: Nome do arquivo de backup (opcional)
            compressao: Tipo de compressão ('gz', 'bz2', 'xz')
        
        Returns:
            Caminho do arquivo de backup criado
        """
        caminho_origem = Path(caminho_origem)
        
        if not caminho_origem.exists():
            logger.error(f"Caminho não existe: {caminho_origem}")
            return None
        
        extensoes = {'gz': '.tar.gz', 'bz2': '.tar.bz2', 'xz': '.tar.xz'}
        extensao = extensoes.get(compressao, '.tar.gz')
        
        if nome_backup is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_backup = f"backup_{caminho_origem.name}_{timestamp}{extensao}"
        
        arquivo_backup = self.local_primario / nome_backup
        
        try:
            modo = f'w:{compressao}' if compressao else 'w'
            with tarfile.open(arquivo_backup, modo) as tar:
                tar.add(caminho_origem, arcname=caminho_origem.name)
            
            logger.info(f"Backup TAR criado: {arquivo_backup}")
            return arquivo_backup
        
        except Exception as e:
            logger.error(f"Erro ao criar backup TAR: {e}")
            return None
    
    def implementar_regra_3_2_1(self, arquivo_backup):
        """
        Implementa a regra 3-2-1 para o arquivo de backup.
        
        Args:
            arquivo_backup: Caminho do arquivo de backup
        """
        arquivo_backup = Path(arquivo_backup)
        
        if not arquivo_backup.exists():
            logger.error(f"Arquivo de backup não encontrado: {arquivo_backup}")
            return False
        
        try:
            # Cópia 1: Local Primário (já existe)
            logger.info(f"Cópia 1 (Local Primário): {arquivo_backup}")
            
            # Cópia 2: Local Secundário (mídia diferente)
            copia_secundaria = self.local_secundario / arquivo_backup.name
            shutil.copy2(arquivo_backup, copia_secundaria)
            logger.info(f"Cópia 2 (Local Secundário): {copia_secundaria}")
            
            # Cópia 3: Offsite (fora do local)
            copia_offsite = self.offsite / arquivo_backup.name
            shutil.copy2(arquivo_backup, copia_offsite)
            logger.info(f"Cópia 3 (Offsite): {copia_offsite}")
            
            # Registra no manifesto
            info_backup = {
                'timestamp': datetime.now().isoformat(),
                'nome_arquivo': arquivo_backup.name,
                'tamanho_bytes': arquivo_backup.stat().st_size,
                'hash': self.calcular_hash_arquivo(arquivo_backup),
                'locais': [
                    str(arquivo_backup),
                    str(copia_secundaria),
                    str(copia_offsite)
                ]
            }
            
            self.manifesto['backups'].append(info_backup)
            self.salvar_manifesto()
            
            logger.info("Regra 3-2-1 implementada com sucesso")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao implementar regra 3-2-1: {e}")
            return False
    
    def verificar_integridade_backup(self, arquivo_backup):
        """
        Verifica a integridade de um arquivo de backup.
        
        Args:
            arquivo_backup: Caminho do arquivo de backup
        
        Returns:
            True se íntegro, False caso contrário
        """
        arquivo_backup = Path(arquivo_backup)
        
        try:
            if arquivo_backup.suffix == '.zip':
                with zipfile.ZipFile(arquivo_backup, 'r') as zipf:
                    resultado = zipf.testzip()
                    if resultado is None:
                        logger.info(f"Backup ZIP íntegro: {arquivo_backup}")
                        return True
                    else:
                        logger.error(f"Arquivo corrompido no ZIP: {resultado}")
                        return False
            
            elif arquivo_backup.suffix in ['.gz', '.bz2', '.xz'] or '.tar' in arquivo_backup.name:
                with tarfile.open(arquivo_backup, 'r:*') as tar:
                    resultado = tar.getmembers()
                    logger.info(f"Backup TAR íntegro: {arquivo_backup}")
                    return True
        
        except Exception as e:
            logger.error(f"Erro ao verificar integridade: {e}")
            return False
    
    def listar_backups(self):
        """Lista todos os backups realizados."""
        print("\n" + "=" * 80)
        print("BACKUPS REALIZADOS")
        print("=" * 80)
        
        for i, backup in enumerate(self.manifesto['backups'], 1):
            print(f"\n{i}. {backup['nome_arquivo']}")
            print(f"   Data: {backup['timestamp']}")
            print(f"   Tamanho: {backup['tamanho_bytes'] / (1024**2):.2f} MB")
            print(f"   Hash: {backup['hash'][:16]}...")
            print(f"   Locais:")
            for local in backup['locais']:
                print(f"     - {local}")
    
    def restaurar_backup(self, nome_arquivo, diretorio_destino='.'):
        """
        Restaura um backup.
        
        Args:
            nome_arquivo: Nome do arquivo de backup
            diretorio_destino: Diretório onde restaurar
        """
        # Procura o arquivo nos três locais
        locais_busca = [self.local_primario, self.local_secundario, self.offsite]
        arquivo_encontrado = None
        
        for local in locais_busca:
            arquivo_candidato = local / nome_arquivo
            if arquivo_candidato.exists():
                arquivo_encontrado = arquivo_candidato
                break
        
        if not arquivo_encontrado:
            logger.error(f"Arquivo de backup não encontrado: {nome_arquivo}")
            return False
        
        try:
            diretorio_destino = Path(diretorio_destino)
            diretorio_destino.mkdir(exist_ok=True)
            
            if arquivo_encontrado.suffix == '.zip':
                with zipfile.ZipFile(arquivo_encontrado, 'r') as zipf:
                    zipf.extractall(diretorio_destino)
            
            elif '.tar' in arquivo_encontrado.name:
                with tarfile.open(arquivo_encontrado, 'r:*') as tar:
                    tar.extractall(diretorio_destino)
            
            logger.info(f"Backup restaurado em: {diretorio_destino}")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            return False
    
    def limpar_backups_antigos(self, dias=30):
        """
        Remove backups mais antigos que o número de dias especificado.
        
        Args:
            dias: Número de dias para manter backups
        """
        from datetime import timedelta
        
        data_limite = datetime.now() - timedelta(days=dias)
        backups_removidos = 0
        
        for backup in self.manifesto['backups'][:]:
            data_backup = datetime.fromisoformat(backup['timestamp'])
            
            if data_backup < data_limite:
                # Remove os arquivos
                for local in backup['locais']:
                    arquivo = Path(local)
                    if arquivo.exists():
                        arquivo.unlink()
                        logger.info(f"Arquivo removido: {arquivo}")
                
                # Remove do manifesto
                self.manifesto['backups'].remove(backup)
                backups_removidos += 1
        
        self.salvar_manifesto()
        logger.info(f"Total de backups antigos removidos: {backups_removidos}")


def main():
    """Função principal para demonstração."""
    print("Sistema de Backup Automatizado")
    print("=" * 80)
    
    # Criar instância do sistema de backup
    backup_system = SistemaBackup()
    
    # Exemplo: criar um diretório de teste
    diretorio_teste = Path('./dados_teste')
    diretorio_teste.mkdir(exist_ok=True)
    
    # Criar alguns arquivos de teste
    for i in range(3):
        arquivo = diretorio_teste / f'arquivo_{i}.txt'
        arquivo.write_text(f'Conteúdo do arquivo {i}\n' * 100)
    
    print(f"\nDiretório de teste criado: {diretorio_teste}")
    
    # Criar backup ZIP
    print("\n1. Criando backup em formato ZIP...")
    backup_zip = backup_system.criar_backup_zip(diretorio_teste)
    
    if backup_zip:
        # Implementar regra 3-2-1
        print("\n2. Implementando regra 3-2-1...")
        backup_system.implementar_regra_3_2_1(backup_zip)
        
        # Verificar integridade
        print("\n3. Verificando integridade do backup...")
        backup_system.verificar_integridade_backup(backup_zip)
        
        # Listar backups
        backup_system.listar_backups()
    
    print("\n" + "=" * 80)
    print("Sistema de Backup finalizado")


if __name__ == '__main__':
    main()
