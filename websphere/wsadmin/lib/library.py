#
# Configuration du proxy HTTP et HTTPS
#
# @param jvm jvm concern�e
# @param nonProxyHosts liste des sites avec acc�s direct, s�par�s par des virgules.
# @param proxyHost adresse du proxy
# @param proxyPort port du proxy
#
def configureProxy(jvm, nonProxyHosts, proxyHost, proxyPort) :
	sys.stdout.write('Configuration du proxy\n')
	# Proxy HTTP
	configureSystemProperty(jvm, 'http.proxySet', 'true', 'false', 'http.proxySet')
	configureSystemProperty(jvm, 'http.proxyHost', proxyHost, 'false', 'http.proxyHost')
	configureSystemProperty(jvm, 'http.proxyPort', proxyPort, 'false', 'http.proxyPort')
	if not nonProxyHosts :
		configureSystemProperty(jvm, 'http.nonProxyHosts', nonProxyHosts, 'false', 'http.nonProxyHosts')
	# Proxy HTTPS
	configureSystemProperty(jvm, 'https.proxySet', 'true', 'false', 'https.proxySet')
	configureSystemProperty(jvm, 'https.proxyHost', proxyHost, 'false', 'https.proxyHost')
	configureSystemProperty(jvm, 'https.proxyPort', proxyPort, 'false', 'https.proxyPort')
	if not nonProxyHosts :
		configureSystemProperty(jvm, 'https.nonProxyHosts', nonProxyHosts, 'false', 'https.nonProxyHosts')
	sys.stdout.write('Configuration du proxy termin�e.\n')
# end configureProxy()

#
# Configuration d'une propri�t� syst�me de la JVM
#
# @param jvm jvm concern�e
# @param value valeur de la propri�t�
# @param required la propri�t� est-elle obligatoire
# @param description description de la propri�t�
#
def configureSystemProperty(jvm, name, value, required, description):
	attr_name  = ['name', name]
	attr_value = ['value', value]
	attr_required = ['required', required]
	attr_description = ['description', '']
	attr_list = [attr_name, attr_value, attr_required, attr_description]
	property=['systemProperties',[attr_list]]
	AdminConfig.modify(jvm, [property])
# end configureSystemProperty()

#
# Cr�ation d'une source de donn�es Teradata
#
# @param nodeName nom du noeuds sur lequel la source de donn�es doit �tre cr��e.
# @param jdbcDriverClasspath
# @param name nom de la source de donn�es
# @param description description
# @param jndiName nom JNDI
# @param user identifiant d'acc�s � la base de donn�es
# @param password mots de passe d'acc�s � la base de donn�es
# @param DSName nom de la base de donn�es
#
def createTeradataDataSource(nodeName, jdbcDriverClasspath, jdbcDriverClasspathValue, name, description, jndiName, user, password, DSName) :
	sys.stdout.write('Cr�ation de la source de donn�es Teradata\n')
	node = AdminConfig.getid('/Node:' + nodeName + '/')
	# Cr�ation ou mise � jour de la variable Websphere TERADATA_JDBC_DRIVER_PATH
	createOrUpdateWebsphereVariable(nodeName, 'TERADATA_JDBC_DRIVER_PATH', jdbcDriverClasspath)
	# Cr�ation du fournisseur JDBC pour Teradata
	providerType = ['providerType', 'User-defined JDBC Provider']
	providerName = ['name', 'TERADATA JDBC Driver']
	implClassName = ['implementationClassName', 'com.teradata.jdbc.TeraConnectionPoolDataSource']
	classpath = ['classpath', jdbcDriverClasspathValue] 
	jdbcAttrs = [providerType, providerName, implClassName, classpath]
	provider = AdminConfig.create('JDBCProvider', node, jdbcAttrs) 
	# Cr�ation de la source de donn�es
	dsAttrs = [['name', name], ['description', description], ['jndiName', jndiName], ['datasourceHelperClassname','com.ibm.websphere.rsadapter.GenericDataStoreHelper']]
	ds = AdminConfig.create('DataSource', provider, dsAttrs)
	# Ajout des propri�t�s personalis�es
	dsPropSet = AdminConfig.create('J2EEResourcePropertySet', ds, [])
	AdminConfig.create('J2EEResourceProperty', dsPropSet, [['name', 'user'], ['type', 'java.lang.String'], ['value', user]])
	AdminConfig.create('J2EEResourceProperty', dsPropSet, [['name', 'password'], ['type', 'java.lang.String'], ['value', password]])
	AdminConfig.create('J2EEResourceProperty', dsPropSet, [['name', 'DSName'], ['type', 'java.lang.String'], ['value', DSName]])
	AdminConfig.create('J2EEResourceProperty', dsPropSet, [['name', 'charSet'], ['type', 'java.lang.String'], ['value', 'UTF8']])
	sys.stdout.write('Cr�ation de la source de donn�es Teradata termin�e\n')
# end createTeradataDataSource

#
# Cr�ation d'une source de donn�es Teradata
#
# @param nodeName nom du noeuds sur lequel la source de donn�es doit �tre cr��e.
# @param jdbcDriverPath
# @param jdbcDriverClasspath
# @param name
# @param description
# @param jndiName
# @param user
# @param password
# @param jdbcUrl
#
def createOracleDataSource(nodeName, jdbcDriverPath, jdbcDriverClasspath, name, description, jndiName, user, password, jdbcUrl):
	sys.stdout.write('Cr�ation de la source de donn�es Oracle...\n')
	node = AdminConfig.getid('/Node:' + nodeName + '/') 
	# Cr�ation ou mise � jour de la variable Websphere TERADATA_JDBC_DRIVER_PATH
	createOrUpdateWebsphereVariable(nodeName, 'ORACLE_JDBC_DRIVER_PATH', jdbcDriverPath)
	# Cr�ation de l'entr�e J2C pour la connexion Oracle
	security = AdminConfig.getid('/Security:/')
	jaasAttrs = [['alias', user], ['userId', user], ['password', password]] 
	jaasAuthData = AdminConfig.create('JAASAuthData', security, jaasAttrs)
	# Cr�ation du fournisseur JDBC pour Oracle
	providerType = ['providerType', 'Oracle JDBC Driver (XA)']
	providerName = ['name', 'Oracle JDBC Driver (XA)']
	providerDescription = ['description','Oracle JDBC Driver (XA)']
	providerImplClassName = ['implementationClassName', 'oracle.jdbc.xa.client.OracleXADataSource']
	providerClasspath = ['classpath', jdbcDriverClasspath]
	jdbcAttrs = [providerType, providerName, providerDescription, providerImplClassName, providerClasspath]
	provider = AdminConfig.create('JDBCProvider', node, jdbcAttrs)
	# Cr�ation de la source de donn�es Oracle
	name = ['name', name]
	description = ['description', description]
	jndiName = ['jndiName', jndiName]
	dsora10g = ['datasourceHelperClassname','com.ibm.websphere.rsadapter.Oracle11gDataStoreHelper']
	authDataAlias = ['authDataAlias', user]
	dsAttrs = [name, description, jndiName, dsora10g , authDataAlias, ['providerType', 'Oracle JDBC Driver (XA)']]
	dataSourceTemplate = AdminConfig.listTemplates('DataSource', 'Oracle JDBC Driver XA DataSource')
	ds = AdminConfig.createUsingTemplate('DataSource', provider, dsAttrs, dataSourceTemplate)
	# url JDBC
	dsPropAttrib = [['name', 'URL'], ['type', 'java.lang.String'], ['value', jdbcUrl]]
	dsPropSet = AdminConfig.create('J2EEResourcePropertySet', ds, [])
	AdminConfig.create('J2EEResourceProperty', dsPropSet, dsPropAttrib)
	sys.stdout.write('Cr�ation de la source de donn�es Oracle termin�e.\n')
# end createOracleDataSource()

# 
# Cr�ation ou mise � jour d'une variable Websphere
# 
# @param nodeName nom du noeuds sur lequel la variable doit �tre mise � jour ou cr��e.
# @param symbolicName nom de la variable
# @param value valeur de la variable
#
def createOrUpdateWebsphereVariable(nodeName, symbolicName, value):
	node = AdminConfig.getid('/Node:' + nodeName + '/')
	varSubstitutions = AdminConfig.list('VariableSubstitutionEntry',node).split(java.lang.System.getProperty('line.separator'))
	updated = False
	# recherche de la variable et mise � jour si elle existe
	for varSubst in varSubstitutions:
		getVarName = AdminConfig.showAttribute(varSubst, 'symbolicName')
		if getVarName == symbolicName:
			AdminConfig.modify(varSubst,[['value', value]])
			updated = True
			break
	# cr�ation d la variable si elle n'existe pas.
	if updated == False :
		varmap = AdminConfig.getid('/Node:' + nodeName + '/VariableMap:/')
		AdminConfig.create("VariableSubstitutionEntry", varmap, [["symbolicName", symbolicName],["value", value]])
# end createOrUpdateWebsphereVariable

#
# Retourne le port du endPoint sp�cifi�
#
# @param endPointName nom du endPoint dont on veut conna�tre le port.
#
def getPort(endPointName):
	sepString = AdminConfig.showAttribute(AdminConfig.list('ServerEntry'), 'specialEndpoints')
	sepList = sepString[1:len(sepString)-1].split(' ')
	for specialEndPoint in sepList:
		endPointNm = AdminConfig.showAttribute(specialEndPoint, "endPointName")
		if endPointNm == endPointName:
			ePoint = AdminConfig.showAttribute(specialEndPoint, "endPoint")
			port = AdminConfig.showAttribute(ePoint, "port")
			return port
			break
# end getPort()