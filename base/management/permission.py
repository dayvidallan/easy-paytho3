# -*- coding: utf-8 -*-

# O processo de permissões:
# O script deve ter opções para:
#    - Resetar todas as permissões (padrão)
#    - Somente garantir as permissões dos grupos
#    - Poder escolher a aplicação a resetar/atualizar permissões
#    - Validar se o grupo já foi definido
#    - Validar duplicidade de permissão em um mesmo grupo
#    - Colocar uma opção force para efetuar as operações indepente das Warnings

from xml.dom import minidom
from os.path import isfile


def obter_texto(node_list):
    rc = ""
    for node in node_list:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def obter_por_nome_tag(node_list, tagName):
    for node in node_list:
        if node.nodeType == node.ELEMENT_NODE and node.tagName == tagName:
            return node
    return None

    
class App:
    def __init__(self, nome=None):
        self.nome = nome
        self.grupos = {}
        

class Grupo:
    def __init__(self, nome=None, app=None):
        self.nome = nome
        self.app = app
        self.permissoes = []
        

class Permissao:
    def __init__(self, model_app, model_name, permission_name):
        self.nome = u"%s.%s.%s" % (model_app, model_name, permission_name)
    

class GroupPermission:
    def __init__(self):
        self.apps = {}
        self.nomes_grupo = {}

    def processar(self, nome_arquivo_permissao, current_app):
        dom = minidom.parse(nome_arquivo_permissao).documentElement
        permissoes = []
        # Start process permission file
        for group in dom.getElementsByTagName("group"):
            group_names = obter_texto(group.getElementsByTagName("name")[0].childNodes).split(';')
            # Se tiver a tag app do grupo
            group_app_tag = obter_por_nome_tag(group.childNodes, 'app')
            if group_app_tag:
                group_names_app = (obter_texto(obter_por_nome_tag(group.childNodes, 'app').childNodes) or current_app).split(';')
                
                # se não tiver a mesma quantidade
                if len(group_names) != len(group_names_app):
                    raise Exception('In %s/permission.xml group name %s or apps %s has no app correctly defined' % (current_app, group_names, group_names_app))
                
            for index, group_name in enumerate(group_names):
                group_name = group_name.strip()
                    
                # Caso não tenha definito a app, a app defaul será a do permissions.xml 
                group_app = current_app
                if group_app_tag:
                    group_app = group_names_app[index].strip()
                    
                if group_name in self.nomes_grupo and self.nomes_grupo[group_name].app != group_app:
                    raise Exception('In %s/permission.xml group name %s has been defined in module %s' % (current_app, group_names, self.nomes_grupo[group_name].app))
                
                # se já estiver adicionado recupere                
                if group_app in self.apps:
                    app = self.apps[group_app]
                else:
                    # se não, crie e já adicione
                    app = App(group_app)
                    self.apps[group_app] = app
                
                # se já estiver adicionado recupere   
                if group_name in app.grupos:
                    grupo = app.grupos[group_name]
                else:
                    # se não, crie e já adicione
                    grupo = Grupo(group_name, group_app)
                    app.grupos[group_name] = grupo
                    self.nomes_grupo[group_name] = grupo
                
                
                tags_models = group.getElementsByTagName("models")
                tags_model = group.getElementsByTagName("model")
                
                if tags_models.length > 1:
                    raise Exception(to_ascii(u'Nao deve haver mais de uma tag models em uma tag group => %s[%s]' % (nome_arquivo_permissao, group_name)))
                elif tags_models.length == 1:
                    if tags_model.length == 0:
                        raise Exception(to_ascii(u'Deve haver ao menos de uma tag model em uma tag models => %s[%s]' % (nome_arquivo_permissao, group_name)))
                elif tags_models.length == 0:
                    if tags_model.length != 0:
                        raise Exception(to_ascii(u'A tag model deve estar em uma tag models => %s[%s]' % (nome_arquivo_permissao, group_name)))
                
                # Process permissions
                for model in tags_model:
                    model_app = obter_texto(model.getElementsByTagName("app")[0].childNodes)
                    model_name = obter_texto(model.getElementsByTagName("name")[0].childNodes)
                    for permission in model.getElementsByTagName("permission"):
                        permission_name = obter_texto(permission.childNodes)
                        permissao = Permissao(model_app, model_name, permission_name)
                        grupo.permissoes.append(permissao)
                        permissoes.append(permissao.nome)
        return permissoes
                        
    def obter_grupos(self):
        retorno = []
        for app in self.apps.values():
            for grupo in app.grupos.values():
                retorno.append(grupo)
                               
        return retorno
                        
    def obter_dicionario(self):
        retorno = {}
        for grupo in self.obter_grupos():
            nome_grupo = grupo.nome
            retorno[nome_grupo] = []
            for permissao in grupo.permissoes:
                retorno[nome_grupo].append(permissao.nome)
                    
        return retorno
                        
    @classmethod
    def obter_grupos_por_app(cls, app):
        groups = set()
        permission_file_name = '%s/permissions.xml' % app
        if isfile(permission_file_name):
            dom = minidom.parse(permission_file_name).documentElement
            
            for group in dom.getElementsByTagName("group"):
                group_names = obter_texto(group.getElementsByTagName("name")[0].childNodes).split(';')
                # Se tiver a tag app do grupo
                group_app_tag = obter_por_nome_tag(group.childNodes, 'app')
                if group_app_tag:
                    group_names_app = (obter_texto(obter_por_nome_tag(group.childNodes, 'app').childNodes) or app).split(';')
                    # se não tiver a mesma quantidade
                    if len(group_names) != len(group_names_app):
                        raise Exception('In %s/permission.xml group name %s has no app correctly defined' % (app, group_names))
                    
                for index, group_name in enumerate(group_names):
                    group_name = group_name.strip()
                    group_app = app
                    if group_app_tag:
                        group_app = group_names_app[index].strip()
                        
                    if group_app == app:
                        groups.add(group_name)
                    
        return groups

def to_ascii(txt, codif='utf-8'):
    if not isinstance(txt, basestring):
        txt = unicode(txt)
    if isinstance(txt, unicode):
        txt = txt.encode('utf-8')
    return normalize('NFKD', txt.decode(codif)).encode('ASCII', 'ignore')