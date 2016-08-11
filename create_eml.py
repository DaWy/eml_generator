#!/usr/bin/python
#Autor: David Martin
#Descripcio: Script que genera fitxers UML a partir dels fitxers de correu del servidor de correu (DOVECOT)
def main():
	import os
	import shutil
	import re
	import sys

	#Comprovem Arguments
	if(len(sys.argv)==1):
		print("ERROR: Indica el mode que vols per parametre.")
		print("Mode: directe -> Extreu UML del directori passat per parametre")
		print(str(sys.argv[0])+" <mode> <or_dir> <go_dir> [any_emails]")
		print("Mode: fitxer -> Extreu UML del directori del servidor indicat en la configuracio del fitxer")
		exit()
	else:
		if(sys.argv[1] == "directe"):
			if(len(sys.argv) < 4 or len(sys.argv) > 5):
				print("ERR: Revisa els parametres de la comanda")
				exit()
			else:
				if(os.path.exists(sys.argv[2])):
					or_dir = sys.argv[2]
				else:
					print("ERROR: El directori d'origen no existeix o no es valid!")
					exit()
				go_dir = sys.argv[3]
				#S'ha indicat l'any de copia dels mails
				if(len(sys.argv)==5):
					if(is_number(sys.argv[4])):
						mail_year = sys.argv[4]
						print("FILTRE D'ANY ACTIVAT: "+mail_year)
					else:
						print("ERROR: L'any indicat no es valid!")
						exit()
				else:
					mail_year = ""

			use_txt_config = 'false'

		elif(sys.argv[1] == "fitxer"):
				use_txt_config = 'true'
		else:
				print("ERROR: Parametres incorrectes. Revisa les opcions.")
				exit()
	
	if(use_txt_config == 'true'):
		#Configuracions
		mail_account	= 'recambios'				#Nom del compte de correu del cual volem generar els EML
		go_dir			= '/home/public/eml/'		#Directori a on es colocara l'estructura de EML
		dir_vmail 		= '/home/vmail/masias.com'	#Directori de les dades del servidor de correu
		mail_year		= '2013'					# Any de Correus a Extreure (Per defecte, TOTS)
		#Comprovem config
		print '- Mail Account: '+mail_account+'@masias.com'
		if(os.path.exists('/home/vmail/masias.com/'+mail_account)):
			print '-> (OK!)\n'
		else:
			print '(NO EXISTEIX! - Sortint...)'
			exit()

		go_dir = go_dir + mail_account
		go_dir = go_dir + '/' + mail_year+'/'

	
	#Carreguem configuracio extra
	exclude_dirs 	= ['dovecot.', 'dovecot-', '.Junk', 'spam', '.Correo','maildirfolder']
	do_it 		= 'enabled'			# -> "enabled" Extreu  EML -> "disabled" Mode TEST

	print '- Go Dir: '+go_dir
	if(os.path.exists(go_dir)):
		print '-> (OK!)\n'
	else:
		if(go_dir!=""):
			print '(NO EXISTEIX!)'
			opcio = raw_input("Vols crear el directori: "+go_dir+" ? (s/n)")
			if(opcio.lower() == "s"):
				os.makedirs(go_dir)
			else:
				print "No hi ha directori de desti! Halt!!"
				exit()
		else:
			print "No s'ha definit directori de desti! Halt!!"
			exit()

	if(use_txt_config == 'true'):
		#Comprovem Configuracio
		print "**Configuracio**"
		print "-: Compte de Coreu: "+mail_account
		print "-: Directori de Desti: "+go_dir
		if(mail_year == ''):
			print "-: Any: TOTS"
		else:
			print "-: Any: "+mail_year
		print "-: Directori de Mails: "+dir_vmail
	
		opcio = raw_input('Es correcta la configuracio? (s/n):') 
		if(opcio.lower()!="s"):
			print "Halt! Sortint..."
			exit()
	
		work_dir = dir_vmail + '/'+ mail_account + '/Maildir'
		filedirs = os.listdir(work_dir)
	else:
		work_dir = or_dir

	contamails = 0
	contarxius = 0
	contafails = 0
	failed = []

	
	for root, dirs, files in os.walk(work_dir):
		if(use_txt_config == 'true'):
			directori = root.replace('/home/vmail/masias.com/'+mail_account+'/Maildir','')
		else:
			directori = root.replace(or_dir,'')
		print 'Directori actual: '+directori
		directori = directori.replace('.','/')
 		for arxius in files:
			contarxius = contarxius + 1
			if(doit(arxius,exclude_dirs)==1):
				if(not os.path.exists(go_dir+directori)):
					if(do_it=='enabled'):
						os.makedirs(go_dir+directori)
				if(not os.path.isfile(go_dir+directori+arxius)):
					content = ""
					f = open(root+'/'+arxius)
					for line in f:
						content += line
					cadena = re.search('[M|T|W|F|S]{1}[a-z]{2},\s+[0-9]{1,2}\s[A-Z][a-z]{2}\s[0-9]{4}',content)
					if(cadena!=None):
						contamails = contamails + 1
						mailname = cadena.group()
						mailname = mailname.strip(' \t\n')
						mailname = mailname.replace(',','')
						mailname = mailname.replace(' ','-')
						mailname = mailname.replace('--','-')
						mailname = getMailString(mailname)
						sub_s = re.search('Subject:.+',content)
						if(sub_s!=None):
							assumpte = sub_s.group()
						else:
							assumpte = "NULL"
						assumpte = assumpte.replace("Subject:","")
						assumpte = parseCode(assumpte) #Parsejem el Codi del Asumpte
						if(len(assumpte)>220):
							assumpte = assumpte[:220] #Limitacio arxius Windows
						if(do_it=="enabled"):
							if(getMailYear(mailname)==mail_year or mail_year == ""):
								print str(contamails)+' : => '+mailname+' => '+assumpte
								if(directori[-3:]=="cur"):
									directori_dest = directori+"/.."
									remove = 1
								else:
									directori_dest = directori
								if(not os.path.exists(go_dir+directori_dest+'/'+mailname+'.'+assumpte+'.'+str(contamails)+'.eml')):
									shutil.copy(root+'/'+arxius,go_dir+directori_dest)
									shutil.move(go_dir+directori_dest+'/'+arxius,go_dir+directori_dest+'/'+mailname+'.'+assumpte+'.'+str(contamails)+'.eml')
						else:
							print str(contamails)+' : TEST_MODE'
					else:
						print 'FAILED : '+arxius
						contafails = contafails +1
					failed.append(arxius)
	#Final. Donem permisos publics y Eliminem els directoris vacios cur
	import commands
	(status, output) = commands.getstatusoutput("chmod -R o+rwx "+go_dir)
	(status, output) = commands.getstatusoutput("find "+go_dir+" -type d -empty -print0 | xargs -0 rmdir")

	print 'Correus Fallats: '
	print 'Total de Mails Fallats: '+str(contafails)
	print 'Total de Mails Procesats: '+str(contamails)
	print 'Total de Arxius: '+str(contarxius)

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False


def parseCode(codi):
	parse = ""
	premove = [':','*','/','?','"']
	if(codi.find("iso-8859-1")!=-1 or codi.find("ISO-8859-1")!=1):
		dict = {}
		dict['E0'] = chr(224)
		dict['E1'] = chr(225)
		dict['E8'] = chr(232)
		dict['E9'] = chr(233)
		dict['ED'] = chr(237)
		dict['EE'] = chr(238)
		dict['F2'] = chr(242)
		dict['F3'] = chr(243)
		dict['FA'] = chr(250)
		dict['FB'] = chr(251)
		dict['E7'] = chr(231)
		dict['C7'] = chr(199)
		dict['C0'] = chr(192)
		dict['C1'] = chr(193)
		dict['C8'] = chr(200)
		dict['C9'] = chr(201)
		dict['CC'] = chr(204)
		dict['CD'] = chr(205)
		dict['D2'] = chr(210)
		dict['D3'] = chr(211)
		dict['D9'] = chr(217)
		dict['DA'] = chr(218)
		for key in dict.keys():
			codi = codi.replace("="+key,dict[key])
	codi = codi.replace("iso-8859-1","")
	codi = codi.replace("ISO-8859-1","")
	codi = codi.replace("=?","")
	codi = codi.replace("?=","")
	codi = codi.replace("?Q?","")
	codi = codi.replace("?q?","")
	codi = codi.replace("?b?","")
	codi = codi.replace("?B?","")

	for char in premove:
		codi = codi.replace(char, "_")
	return codi


def doit(file,excludes):
	for ex in excludes:
		if(file.find(ex)!=-1):
			return -1
	return 1

def getMailString(mailname):
	import re
	month = re.search('[A-Z][a-z]{2}',mailname[4:])
	mes = month.group()
	if(mes == "Jan"):
		cadena = mailname.replace("Jan","1")
	if(mes == "Feb"):
		cadena = mailname.replace("Feb","2")
	if(mes == "Mar"):
		cadena = mailname.replace("Mar","3")
	if(mes == "Apr"):
		cadena = mailname.replace("Apr","4")
	if(mes == "May"):
		cadena = mailname.replace("May","5")
	if(mes == "Jun"):
		cadena = mailname.replace("Jun","6")
	if(mes == "Jul"):
		cadena = mailname.replace("Jul","7")
	if(mes == "Aug"):
		cadena = mailname.replace("Aug","8")
	if(mes == "Sep"):
		cadena = mailname.replace("Sep","9")
	if(mes == "Oct"):
		cadena = mailname.replace("Oct","10")
	if(mes == "Nov"):
		cadena = mailname.replace("Nov","11")
	if(mes == "Dec"):
		cadena = mailname.replace("Dec","12")

	cadena = cadena.replace("Mon-","")
	cadena = cadena.replace("Tue-","")
	cadena = cadena.replace("Wed-","")
	cadena = cadena.replace("Thu-","")
	cadena = cadena.replace("Sun-","")
	cadena = cadena.replace("Sat-","")
	cadena = cadena.replace("Fri-","")
	
	any_s = re.search('-[0-9]{4}',cadena)
	any = any_s.group().replace("-","")

	mes_s = re.search('-[0-9]{1,2}-',cadena)
	mes = mes_s.group().replace("-","")

	dia_s = re.search('[0-9]{1,2}-',cadena)
	dia = dia_s.group().replace("-","")
	
	
	return any+'-'+mes+'-'+dia
	
def getMailYear(mailname):
	return mailname[:4]

if __name__ == "__main__":
	main()
