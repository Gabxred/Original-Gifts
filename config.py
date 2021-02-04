from flask import Flask, request, jsonify, redirect, url_for
import json
import sqlite3
from flask import g, render_template
from base64 import b64encode,b64decode

from flask import make_response
#pip install numpy
#Profesor Ruben Sanabria: es recomendable la version de numpy 1.19.4 pues las versiones anteriores
#han generado un problema en varias partes del proyecto
#programado en python 3.7.5 32bits
import numpy as np
import datetime
import pdfkit

app = Flask(__name__,template_folder="")
UPLOAD_FOLDER = '/path/to/static/images'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH']=20
#constructores posee valor del usuario con sesion abierta
class usuario:
     def __init__( self,usuar, idusuario, nivel,correo, contrasena,numero,estado):
         self.usuar=usuar
         self.idusaurio=idusuario
         self.nivel=nivel
         self.contrasena=contrasena
         self.numero=numero
         self.correo=correo
         self.estado=estado



user= usuario(0,0,0,0,0,0,0)


#aqui  poner la ruta de donde eta la base  de datos sqlite llamado tienda
#utilizar "/" en vez de "\"
DATABASE = 'C:/Users/MELO/Desktop/8vo Semestre/Aplicaciones web/3erparcial/Original Gifs/original gifs/tienda.db'
tuplaproducto=["","","","","",""]
tuplaprecios=["","","","","",""]

#instalar el wkhtmltopdf de aqui:https://wkhtmltopdf.org/downloads.html
#configuracion del wkhtmltopdf: Aqui poner la ubicacion del wkhtmltopdf.exe

path_wkhtmltopdf = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
#pdfkit.from_url("http://google.com", "out.pdf", configuration=config)

#reporte 1
@app.route('/reporte1')
def report():
  
  conn = db_connection()    
  cursor = conn.cursor()
  
  resultValue = cursor.execute("select art.idarticulo, art.nombre, art.precio, art.marca, inv.cantidadarat, cat.nombre from articulo as art, categoria as cat, inventario as inv where art.idcategoria=cat.idcategoria and inv.idinventario=art.idinventario")
  resultValue = cursor.fetchall()
  html = render_template('reporte1.html', invent=resultValue)
  pdf = pdfkit.from_string(html, False, configuration=config)
  response = make_response(pdf)
  response.headers["Content-Type"] = "application/pdf"
  response.headers["Content-Disposition"] = "inline; filename=output.pdf"
  return response


#reporte 2
@app.route('/<int:id>reporte2')
def report2(id):
  
  conn = db_connection()    
  cursor = conn.cursor()
  
  cursor=conn.execute("select art.nombre, aped.cantidad, art.precio from articulo art, articulopedido as aped, pedido as ped where art.idarticulo=aped.idarticulo and aped.idpedido=ped.idpedido and aped.idpedido= "+str(id))
  resultValue=cursor.fetchall()
  conn.commit()
  cursor=conn.execute("SELECT      monto FROM pedidodetalle where idpedido="+str(id))
  total=cursor.fetchone()

  html = render_template('reporte2.html', invent=resultValue,usuar=user.usuar,total=total[0])
  pdf = pdfkit.from_string(html, False, configuration=config)
  response = make_response(pdf)
  response.headers["Content-Type"] = "application/pdf"
  response.headers["Content-Disposition"] = "inline; filename=output.pdf"
  return response

#compra
@app.route('/<int:cond>compras<int:id>', methods=["GET","POST"])
def compras(cond,id):
    error=None
    conn = db_connection()
    cursor = conn.cursor()
    if cond==1:
        account=cursor.execute("SELECT art.nombre,art.precio, inv.idinventario,   inv.cantidadarat, art.imagen FROM articulo AS art, inventario AS inv WHERE inv.idinventario = art.idinventario AND    art.idarticulo ="+str(id))
        account = cursor.fetchone()
        conn.close()
        
        nombre=account[0]
        
        precio=account[1]
        
        idinvent=account[2]
        cantidad=account[3]
        
        img=account[4]
        imagen=b64encode(img).decode("utf-8")
        return render_template("compra.html",producto1=nombre, precio=precio, idinvent=idinvent, cantidad=cantidad,foto=imagen, username=user.usuar, cat=user.nivel,idart=id, )
    else:
        inventarioinicio()
        error=" primero debe iniciar sesion!"
        return render_template('index.html', producto0=tuplaproducto[0],producto1=tuplaproducto[1],producto2=tuplaproducto[2],producto3=tuplaproducto[3],producto4=tuplaproducto[4],producto5=tuplaproducto[5],precio0=tuplaprecios[0],precio1=tuplaprecios[1],precio2=tuplaprecios[2],precio3=tuplaprecios[3],precio4=tuplaprecios[4],precio5=tuplaprecios[5], error=error)

#pedidoanterior
@app.route('/<int:id>pedidoanterior')
def pedant(id):
    error=None
    conn = db_connection()
    cursor = conn.cursor()
    cursor=conn.execute("select ped.idpedido, det.monto, vde.fechaventa from  pedido as ped, pedidodetalle as det, venta as vent, ventadetalle as vde where ped.idpedido=det.idpedido and      det.idpedidodet=vent.idpedidodet and      vent.idventa=vde.idventa and      ped.idusuario="+str(user.idusaurio))
    account= cursor.fetchall()
    conn.commit()
    if id==0:
        
        if account:
            
            return render_template("mispedidos.html",username=user.usuar, cat=user.nivel, invent=account)
        else:
            error="No hay Registros"
            return render_template("mispedidos.html",username=user.usuar, cat=user.nivel, error=error)
    else:
        if account:
            cursor = conn.cursor()
            cursor=conn.execute("select art.nombre, aped.cantidad, art.precio from articulo art, articulopedido as aped, pedido as ped where art.idarticulo=aped.idarticulo and aped.idpedido=ped.idpedido and aped.idpedido= "+str(id))
            account2=cursor.fetchall()
            conn.commit()
            return render_template("mispedidos.html",username=user.usuar, cat=user.nivel, invent=account,tabla2=account2)
        else:
            error="No hay Registros"
            return render_template("mispedidos.html",username=user.usuar, cat=user.nivel, error=error)

        
#ventas
@app.route('/<int:id>venta')
def vent(id):
    error=None
    conn = db_connection()
    cursor = conn.cursor()
    cursor=conn.execute("select ped.idpedido, det.monto, vde.fechaventa, usu.nombre from  pedido as ped, pedidodetalle as det, venta as vent, ventadetalle as vde, usuario as usu where ped.idpedido=det.idpedido and      det.idpedidodet=vent.idpedidodet and      vent.idventa=vde.idventa and      ped.idusuario=usu.idusuario order by vde.fechaventa desc")
    account= cursor.fetchall()
    conn.commit()
    if id==0:
        
       if account:
           return render_template("ventas.html",username=user.usuar, cat=user.nivel, invent=account)
       else:
            error="No hay Registros"
            return render_template("ventas.html",username=user.usuar, cat=user.nivel, error=error)
    else:
        if account:
            cursor = conn.cursor()
            cursor=conn.execute("select art.nombre, aped.cantidad, art.precio from articulo art, articulopedido as aped, pedido as ped where art.idarticulo=aped.idarticulo and aped.idpedido=ped.idpedido and aped.idpedido= "+str(id))
            account2=cursor.fetchall()
            conn.commit()
            return render_template("ventas.html",username=user.usuar, cat=user.nivel, invent=account,tabla2=account2)
        else:
            error="No hay Registros"
            return render_template("ventas.html",username=user.usuar, cat=user.nivel, error=error)
        

#pedidoactual
@app.route('/pedidoactual',methods=["GET","POST"])
def pedactual():
    
    conn = db_connection()
    cursor = conn.cursor()
    cursor=conn.execute("Select idpedido from pedido where idusuario= "+str(user.idusaurio)+" and estado<>'V' and estado<>'C' order by idpedido desc")
    account=cursor.fetchone()
    if account:
        idpedido= account[0]
        cursor=conn.execute("select  art.nombre, arp.cantidad, art.precio, art.idarticulo from articulo as art, articulopedido as arp, pedido as ped where art.idarticulo=arp.idarticulo and ped.idpedido=arp.idpedido and ped.idpedido="+str(idpedido)+" order by art.nombre asc")
        account=cursor.fetchall()
        
        cursor=conn.execute("select arp.cantidad, art.precio from articulo as art, articulopedido as arp, pedido as ped where art.idarticulo=arp.idarticulo and ped.idpedido=arp.idpedido and ped.idpedido="+str(idpedido)+" order by art.nombre asc")
        account2=cursor.fetchall()
        account22= np.array(account2)
        Output = []
        for elem in account22: 
            temp = elem[0]*elem[1] 
            Output.append(temp) 

        var=sum(Output)
        conn.close()
        return render_template("pedidoactual.html", username=user.usuar, cat=user.nivel,tabla=account, total=var)
    else:
        error="asd"
        total=0
        conn.close()
        return render_template("pedidoactual.html", username=user.usuar, total=total, cat=user.nivel,error=error )

#confirmar Pedido
@app.route('/<int:id>estadop<string:bande>')
def estadop(id,bande):
    
    conn = db_connection()
    cursor = conn.cursor()
    cursor=conn.execute("Select idpedido from pedido where idusuario= "+str(user.idusaurio)+" and estado<>'V' and estado<>'C' order by idpedido desc")
    account=cursor.fetchone()
    idpedi=account[0]
    
    if bande=='A':
        cursor=conn.execute("Select idarticulo from articulopedido where idpedido= "+str(idpedi))
        articulos=cursor.fetchall()
        articulo=np.array(articulos)
        conn.commit()
        cursor=conn.execute("Select cantidad from articulopedido where idpedido= "+str(idpedi))
        articulos=cursor.fetchall()
        cantidad=np.array(articulos)
        conn.commit()
        a=0
        
        for x in articulo:
            cursor=conn.execute("Select idinventario from articulo where idarticulo= "+str(x[0]))
            temp2=cursor.fetchone()
            idinvent=temp2[0]
            conn.commit()

            cursor=conn.execute("Select cantidadarat from inventario where idinventario= "+str(idinvent))
            temp2=cursor.fetchone()
            cant=temp2[0]
            cant=str((int(cant)-int(cantidad[a])))
            tuplainvent=(cant,idinvent)
            conn.execute("UPDATE inventario SET   cantidadarat =?  WHERE idinventario= ?",tuplainvent)
            conn.commit()
            a=a+1

        tuplaconpe=(idpedi,str(id))
        conn.execute("INSERT INTO pedidodetalle ( idpedido,  monto   )  VALUES ( ?,?   )",tuplaconpe)
        conn.commit()
        
        cursor=conn.execute("Select idpedidodet from pedidodetalle where idpedido= "+str(idpedi))
        account=cursor.fetchone()
        idet=account[0]
        conn.commit()

        tuplavent=(idet,str(user.idusaurio))
        conn.execute("INSERT INTO venta ( idpedidodet,  idusuario   )  VALUES ( ?,?   )",tuplavent)
        conn.commit()

        cursor=conn.execute("Select idventa from venta where idpedidodet= "+str(idet))
        account=cursor.fetchone()
        ivent=account[0]
        hoy=datetime.datetime.today().strftime('%Y-%m-%d')
        conn.commit()

        tuplaventdet=(ivent,str(id),hoy)
        conn.execute("INSERT INTO ventadetalle ( idventa,  precioventa,fechaventa   )  VALUES ( ?,?,?   )",tuplaventdet)
        conn.commit()
        
        conn.execute("UPDATE pedido SET estado = 'V' WHERE idpedido= "+str(idpedi))
        conn.commit()
        conn.close()

        return redirect(url_for('pedactual'))
    
#eliminar producto del pedido
@app.route('/<int:id>eliminarp')
def elim(id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor=conn.execute("Select idpedido from pedido where idusuario= "+str(user.idusaurio)+" and estado<>'V' and estado<>'C' order by idpedido desc")
    account=cursor.fetchone()
    
    idpedi=account[0]
    
    tuplaelimi=(idpedi,id)
    conn.execute("DELETE FROM articulopedido   WHERE idpedido = ?  AND     idarticulo = ?",(tuplaelimi))
    conn.commit()
    return redirect(url_for('pedactual'))
    
#cancelar pedido
@app.route('/cancelar')
def canc():
    conn = db_connection()
    cursor = conn.cursor()
    cursor=conn.execute("Select idpedido from pedido where idusuario= "+str(user.idusaurio)+" and estado<>'V' and estado<>'C' order by idpedido desc")
    account=cursor.fetchone()
    idpedi=account[0]
    
    tuplacancelado=("C",str(idpedi))
    cursor=conn.execute("UPDATE pedido SET estado= ? WHERE idpedido= ?", tuplacancelado)
    conn.commit()
    conn.close
    return redirect(url_for('pedactual'))




#conexion
def db_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
    except sqlite3.Error as e:
        print(e)
    return conn

#loggin
@app.route('/loggeo', methods=["GET","POST"]) 
def log(): 
    error=None
    conn = db_connection()
    cursor = conn.cursor()
    correo = request.form.get("username") 
    contra = request.form.get("password")
    
    if request.method == "POST":
        cursor = conn.execute("SELECT idusuario, nombre, correo, nivel contrasena FROM usuario  where correo= '"+correo+"' and contrasena= '"+contra+"'")
        account = cursor.fetchone()
        conn.close()
        if account:
             user.idusaurio= account[0]
             user.usuar=account[1]
             user.nivel = account[3]
             return render_template('login.html',username=user.usuar, cat=user.nivel,producto0=tuplaproducto[0],producto1=tuplaproducto[1],producto2=tuplaproducto[2],producto3=tuplaproducto[3],producto4=tuplaproducto[4],producto5=tuplaproducto[5],precio0=tuplaprecios[0],precio1=tuplaprecios[1],precio2=tuplaprecios[2],precio3=tuplaprecios[3],precio4=tuplaprecios[4],precio5=tuplaprecios[5])  
     
        else:
                error="error de credenciales"
                return render_template('index.html', error=error, producto0=tuplaproducto[0],producto1=tuplaproducto[1],producto2=tuplaproducto[2],producto3=tuplaproducto[3],producto4=tuplaproducto[4],producto5=tuplaproducto[5],precio0=tuplaprecios[0],precio1=tuplaprecios[1],precio2=tuplaprecios[2],precio3=tuplaprecios[3],precio4=tuplaprecios[4],precio5=tuplaprecios[5])
    
    if request.method =="GET":
        return  render_template("login.html",username=user.usuar,cat=user.nivel,producto0=tuplaproducto[0],producto1=tuplaproducto[1],producto2=tuplaproducto[2],producto3=tuplaproducto[3],producto4=tuplaproducto[4],producto5=tuplaproducto[5],precio0=tuplaprecios[0],precio1=tuplaprecios[1],precio2=tuplaprecios[2],precio3=tuplaprecios[3],precio4=tuplaprecios[4],precio5=tuplaprecios[5])

#categoria  producto
@app.route('/<int:ident>categoria<int:id>',methods=["GET","POST"])
def categoria(ident,id):
    
    conn = db_connection()
    cursor = conn.cursor()
    cursor = conn.execute("select idarticulo, nombre, descripcion, precio from articulo where idcategoria="+str(id)+" order by nombre asc")
    datos=cursor.fetchall()
    account2=cursor.execute("Select imagen  From articulo where idcategoria="+str(id)+" order by nombre asc")
    account2=cursor.fetchall() 
    fotos= np.array(account2)
    cursor=conn.execute("select nombre from categoria where idcategoria="+str(id))
    dat=cursor.fetchone()
    catp=dat[0]
    conn.close()
    #aqui la magia 64
    for x in range(0,len(fotos)):
        varia=b64encode(fotos[x])
        varia=varia.decode('utf-8')
        fotos[x]= "data:img/png/jpeg;base64,"+varia+" "
    

    account2=fotos.tolist()
    account=zip(datos, account2)
    if ident==1:
        return  render_template ("categorias.html",username=user.usuar, cat=user.nivel,  tabla=account,categoria=catp)
    else:
        return  render_template ("categorias.html",username=0, tabla=account,categoria=catp)
   
        
		    


    



#cuenta cliente/admi
@app.route('/cuent<int:id>',methods=["GET","POST"])
def cuentaadm(id):
    error=None
    conn = db_connection()
    cursor = conn.cursor()
    
    if request.method == "GET":
        cursor = conn.execute("SELECT  nombre, numero, correo, contrasena  contrasena FROM usuario  where idusuario= "+str(id))
        account = cursor.fetchone()
        conn.close()
        if account:             
           nombre=account[0]
           numero=account[1]
           correo=account[2]
           contrasena=account[3]
           return render_template('cuentauser.html',username=user.usuar, nombre=nombre,numero=str(numero),correo=correo,contrasena=contrasena, cat=user.nivel, idusuario=str(id))
        else:
            error='error interno'
            return render_template('cuentauser.html', error= error)
    
    if request.method== 'POST':
        nombre = request.form.get("usuar") 
        contrasena = request.form.get("password")
        correo= request.form.get("correo")
        numero= request.form.get("numero")
        contranew= request.form.get("password2")
        tupla=(nombre,numero,correo,contrasena, id)
        if contrasena== contranew:
            tupla=(nombre,numero,correo,contranew,id)
            cursor=conn.execute("UPDATE usuario   SET nombre = ?,       numero = ?,  correo = ?,       contrasena = ? WHERE idusuario =?",tupla )
            conn.commit()
            error="Actualizada"
            return render_template('cuentauser.html', error=error, username=user.usuar, cat=user.nivel,nombre=tupla[0],numero=str(tupla[1]),correo=tupla[2],contrasena=tupla[3],idusuario=str(id))
        else:
            error="La Contraseña no  es correcta"
            return render_template('cuentauser.html', error=error, username=user.usuar, cat=user.nivel,nombre=tupla[0],numero=str(tupla[1]),correo=tupla[2],contrasena=tupla[3],idusuario=str(id))


#busqueda
@app.route('/search<int:id>', methods=["POST"])
def busqueda(id):
    error=None
    conn = db_connection()
    cursor = conn.cursor()
    produc = request.form.get("buscar")
    
    if produc==None:
        error="no hay"
        if id==1:
            return render_template("busqueda.html", username=user.usuar, cat=user.nivel, error=error)
        else:
            return render_template("busquedasinlog.html", error2=error)
    else: 
        account=cursor.execute("Select art.idarticulo, art.nombre, art.precio, inv.cantidadarat From articulo as art, inventario as inv Where art.idinventario=inv.idinventario and art.nombre like ?",('%'+produc+'%',))
        account=cursor.fetchall() 
        conn.commit()
        if account:
            account2=cursor.execute("Select imagen  From articulo Where nombre like ?",('%'+produc+'%',))
            account2=cursor.fetchall() 
            fotos= np.array(account2)
            
            #aqui la magia 64
            for x in range(0,len(fotos)):
                varia=b64encode(fotos[x])
                varia=varia.decode('utf-8')
                fotos[x]= "data:img/png/jpeg;base64,"+varia+" "
                
            account2=fotos.tolist()
            account=zip(account, account2)
            
            
            if id==1:
                return render_template("busqueda.html", username=user.usuar, cat=user.nivel, tabla=account)
            else:
                return render_template("busquedasinlog.html", error2=error, tabla=account)
        else:
            error="no hay"
            if id==1:
                return render_template("busqueda.html", username=user.usuar, cat=user.nivel, error=error)
            else:
                return render_template("busquedasinlog.html", error2=error)
    
#otros templates
@app.route('/<string:pg>link<int:id>')
def rutas(pg,id):
    if pg=="A":
        if id==1:
            return render_template("galeria.html", username=user.usuar, cat=user.nivel) 
        else:
            return render_template("galeria.html", username=0)
    else:
        if id==1:
            return render_template("contacto.html", username=user.usuar, cat=user.nivel) 
        else:
            return render_template("contacto.html", username=0)
    
    return 0 

#cuenta cliente
@app.route('/cuenta',methods=["GET","POST"])
def cuenta():
    error=None
    conn = db_connection()
    cursor = conn.cursor()
    catego=""
    if request.method == "GET":
        cursor = conn.execute("SELECT  nombre, numero, correo, contrasena, nivel  contrasena FROM usuario  where idusuario= "+str(user.idusaurio))
        account = cursor.fetchone()
        conn.close()
        if account:             
            user.usuar=account[0]
            user.numero=account[1]
            user.correo = account[2]
            user.contrasena=account[3]
            catego=account[4]
            return render_template('cuenta.html',username=user.usuar, nombre=user.usuar,numero=str(user.numero),correo=user.correo,contrasena=user.contrasena, cat=catego)
        else:
            error='error interno'
            return render_template('cuenta.html', error= error)
    
    if request.method== 'POST':
        user.usuar = request.form.get("usuar") 
        user.contrasena = request.form.get("password")
        user.correo= request.form.get("correo")
        user.numero= request.form.get("numero")
        contranew= request.form.get("password2")
        tupla=(user.usuar,user.numero,user.correo,user.contrasena, user.idusaurio)
        if user.contrasena== contranew:
            tupla=(user.usuar,user.numero,user.correo,contranew, user.idusaurio)
            cursor=conn.execute("UPDATE usuario   SET nombre = ?,       numero = ?,  correo = ?,       contrasena = ? WHERE idusuario =?",tupla )
            conn.commit()
            error="Actualizada"
            return render_template('cuenta.html', error=error, username=tupla[0], cat='C',nombre=tupla[0],numero=str(tupla[1]),correo=tupla[2],contrasena=tupla[3])
        else:
            error="La Contraseña no  es correcta"
            return render_template('cuenta.html', error=error, username=tupla[0], cat='C',nombre=tupla[0],numero=str(tupla[1]),correo=tupla[2],contrasena=tupla[3])



#inventario inicio
@app.route('/invent', methods=["GET","POST"])
def invent():
   
    conn = db_connection()
    cursor = conn.cursor()
    cursor = conn.execute("select art.idarticulo, art.nombre, art.precio, art.marca, inv.cantidadarat, cat.nombre from articulo as art, categoria as cat, inventario as inv where art.idcategoria=cat.idcategoria and inv.idinventario=art.idinventario")
    data=cursor.fetchall()
 
    return render_template('inventario.html',username=user.usuar,cat=user.nivel,invent=data)
    
#todos los productos
@app.route('/productos<int:id>', methods=["GET","POST"])
def listaprod(id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor = conn.execute("select idarticulo, nombre, descripcion, precio from articulo order by nombre asc")
    datos=cursor.fetchall()
    account2=cursor.execute("Select imagen  From articulo order by nombre asc")
    account2=cursor.fetchall() 
    fotos= np.array(account2)
        
    #aqui la magia 64
    for x in range(0,len(fotos)):
        varia=b64encode(fotos[x])
        varia=varia.decode('utf-8')
        fotos[x]= "data:img/png/jpeg;base64,"+varia+" "
                
    account2=fotos.tolist()
    datos=zip(datos,account2)
    if id==1:
        return render_template("productosgaleria.html", username=user.usuar,cat=user.nivel,tabla=datos)
    else:
        return render_template("productosgaleria.html", tabla=datos,username=0)
    
 
#inicio carga los datos del index
def inventarioinicio():
    conn = db_connection()
    cursor = conn.cursor()
    #articulo1
    for i in [1,2,3,4,5,6]:
        account=cursor.execute("select nombre, precio from articulo where idarticulo="+str(i))
        account = cursor.fetchone()
        conn.commit()
        tuplaproducto[i-1]=account[0]
        tuplaprecios[i-1]=account[1]

#nuevo cliente/admi
@app.route('/registronuevo<string:id>',methods=["GET","POST"])
def registN(id):
    error=None
    categoria=id
   
    
    if request.method == 'POST':
        idusaurio=request.form.get("idusuar")
        usuario = request.form.get("usuar") 
        contrasena = request.form.get("password")
        correo= request.form.get("correo")
        numero= request.form.get("numero")
        contranew= request.form.get("password2")
        
        if idusaurio=="" or contrasena=="" or correo=="" or usuario=="" or numero=="" or contranew=="":
            error="Complete todos los Espacios"
            return render_template('cuentanueva.html', error=error, username=user.usuar, cat=user.nivel,idtipo=id )
        else:
            if contrasena==contranew:
                conn = db_connection()
                tuplaregistro=(idusaurio,usuario,numero,correo,contrasena,categoria)
                conn.execute("INSERT INTO usuario (idusuario,nombre,numero, correo, contrasena, nivel)VALUES (?,?,?,?,?,?);",tuplaregistro )
                conn.commit()
                error="Creada Correctamente"
                return render_template('cuentanueva.html',username=user.usuar, cat=user.nivel,idtipo=id,error=error)
            else:
                error="la contraseña no es identica"
                return render_template('cuentanueva.html', error=error, username=user.usuar, cat=user.nivel,idtipo=id )
    
    return  render_template('cuentanueva.html', username=user.usuar, cat=user.nivel,idtipo=id )

#borrar usuario
@app.route('/borraruser<int:id>')
def borraruser(id):   
    conn = db_connection()
    conn.execute("DELETE FROM usuario   WHERE idusuario = "+str(id))
    conn.commit()
    return redirect(url_for('admiusr'))

#borrar producto
@app.route('/borrarprod<int:id>')
def borrarprod(id):   
    conn = db_connection()
    conn.execute("DELETE FROM articulo   WHERE idarticulo =  "+str(id))
    conn.commit()
    return redirect(url_for('invent'))


#nuevo cliente
@app.route('/registrar',methods=["GET","POST"])
def regis():
    error=None
   
    if request.method == 'POST':
        user.idusaurio=request.form.get("idusuar")
        user.usuar = request.form.get("usuar") 
        user.contrasena = request.form.get("password")
        user.correo= request.form.get("correo")
        user.numero= request.form.get("numero")
        contranew= request.form.get("password2")
        user.nivel="C"
        if user.idusaurio=="" or user.contrasena=="" or user.correo=="" or user.usuar=="" or user.numero=="" or contranew=="":
            error="Complete todos los Espacios"
            return render_template('registro.html', error2=error)
        else:
            if user.contrasena==contranew:
                conn = db_connection()
                tuplaregistro=(user.idusaurio,user.usuar,user.numero,user.correo,user.contrasena,'C')
                conn.execute("INSERT INTO usuario (idusuario,nombre,numero, correo, contrasena, nivel)VALUES (?,?,?,?,?,?);",tuplaregistro )
                conn.commit()
                
                return render_template('login.html',username=user.usuar, cat='C',producto0=tuplaproducto[0],producto1=tuplaproducto[1],producto2=tuplaproducto[2],producto3=tuplaproducto[3],producto4=tuplaproducto[4],producto5=tuplaproducto[5],precio0=tuplaprecios[0],precio1=tuplaprecios[1],precio2=tuplaprecios[2],precio3=tuplaprecios[3],precio4=tuplaprecios[4],precio5=tuplaprecios[5])
            else:
                error="la contraseña no es identica"
                return render_template("registro.html", error2=error)
            
    return  render_template('registro.html')

#detalleproducto             
@app.route('/<int:id><string:log>', methods=["GET","POST"])
def produc(id,log):
    
    #error=None
    if request.method == "GET":
        conn = db_connection()
        cursor = conn.cursor()
        account=cursor.execute("SELECT  nombre, descripcion,marca,precio,imagen,idarticulo FROM articulo where idarticulo="+str(id))
        account = cursor.fetchone()
        nombre=account[0]
        descr=account[1]
        marca=account[2]
        precio=account[3]
        img=account[4]
        imagen=b64encode(img).decode("utf-8")
        ideart=account[5]
        if log=='Y':
            return render_template('productodetalleY.html', producto1=nombre,precio=precio,descripcion=descr,marca=marca,foto=imagen,username=user.usuar,cat=user.nivel,ideart=ideart)
        else:
            return render_template('productodetalleN.html', producto1=nombre,precio=precio,descripcion=descr,marca=marca,foto=imagen)


#editar Articulo
@app.route('/<int:id>edit', methods=["GET","POST"])
def editprod(id):
    conn = db_connection()
    cursor = conn.cursor()
    error=None
    if request.method=="GET":
        account=cursor.execute("SELECT art.idarticulo, art.nombre,art.descripcion, art.precio,    art.marca,     inv.idinventario,      inv.cantidadarat,      cat.idcategoria, art.imagen FROM articulo AS art,      categoria AS cat,      inventario AS inv WHERE art.idcategoria = cat.idcategoria AND inv.idinventario = art.idinventario AND    art.idarticulo ="+str(id))
        account = cursor.fetchone()
        conn.close()
        idart=account[0]
        nombre=account[1]
        descr=account[2]
        precio=account[3]
        marca=account[4]
        idinvent=account[5]
        cantidad=account[6]
        
        img=account[8]
        imagen=b64encode(img).decode("utf-8")
        return render_template('productoedit.html',username=user.usuar,cat=user.nivel,nombrepro=nombre,descripcion=descr,marca=marca,precio=precio,cantidad=cantidad,foto=imagen,idart=idart)
    
    if request.method=='POST':
        idart=id
        account=cursor.execute("SELECT idinventario FROM articulo WHERE idarticulo ="+str(id))
        account = cursor.fetchone()
        conn.commit()
        idinvent=account[0]
        nombre=request.form.get("nombreprod")
        descr=request.form.get("descripciond")
        precio=request.form.get("preciod")
        marca=request.form.get("marcad")
        categoria=request.form.get("categoriad")
        cantidad=request.form.get("cantidadd")
        
        image=request.files["imagend"]
        
        tuplainvent=(cantidad,  idinvent)
        cursor=conn.execute("UPDATE inventario  SET cantidadarat = ? WHERE idinventario = ?",tuplainvent )
        conn.commit()
        if image.filename=="":
            if categoria=="":
                tupla1=(nombre,descr,marca,precio,id)
                cursor=conn.execute("UPDATE articulo SET  nombre = ?,descripcion = ?,  marca = ?,  precio =? WHERE idarticulo = ?",tupla1)           
                conn.commit()
                error="Actualizado"
                return render_template('productoedit.html',username=user.usuar,cat=user.nivel,nombrepro=nombre,descripcion=descr,marca=marca,precio=precio,cantidad=cantidad,foto=image,ideart=idart, error=error)     
            else:
                
                tuplaA=(categoria, nombre,descr,marca,precio,id)
                cursor=conn.execute("UPDATE articulo SET idcategoria = ?,  nombre = ?,descripcion = ?,  marca = ?,  precio =? WHERE idarticulo = ?",tuplaA)           
                conn.commit()
                error="Actualizado"
                return render_template('productoedit.html',username=user.usuar,cat=user.nivel,nombrepro=nombre,descripcion=descr,marca=marca,precio=precio,cantidad=cantidad,foto=image,ideart=idart, error=error)
        else:
            if categoria=="":        
                image.save(image.filename)
                blob= convertToBinaryData(image.filename)
                tupla2=(nombre,descr,marca,precio,blob,id)
                cursor=conn.execute("UPDATE articulo SET  nombre = ?,descripcion = ?,  marca = ?,  precio =?, imagen=? WHERE idarticulo = ?",tupla2)          
                conn.commit()
                error="Actualizado!"
                imagen=b64encode(blob).decode("utf-8")
                return render_template('productoedit.html',username=user.usuar,cat=user.nivel,nombrepro=nombre,descripcion=descr,marca=marca,precio=precio,cantidad=cantidad,foto=imagen,ideart=idart, error=error)
            else: 
                image.save(image.filename)
                
                blob= convertToBinaryData(image.filename)
                tuplaB=(categoria,nombre,descr,marca,precio,blob,id)
                cursor=conn.execute("UPDATE articulo SET idcategoria = ?,  nombre = ?,descripcion = ?,  marca = ?,  precio =?, imagen= ? WHERE idarticulo = ?",tuplaB)          
                conn.commit()
                error="Actualizado!"
                imagen=b64encode(blob).decode("utf-8")
                return render_template('productoedit.html',username=user.usuar,cat=user.nivel,nombrepro=nombre,descripcion=descr,marca=marca,precio=precio,cantidad=cantidad,foto=imagen,ideart=idart, error=error)


        
#utilizado para convertir las imagenes subidas por el admi a Blob
def convertToBinaryData(filename):
    #Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData
        
#nosotros
@app.route('/about<string:id>')
def nosotros(id):
    if id=="C":
        return render_template("nosotrosC.html",username=user.usuar,cat=user.nivel)
    else:
        return render_template("nosotros.html",username=user.usuar,cat=user.nivel)


#lista de clientes/Admin
@app.route('/adminusr')
def admiusr():
    conn = db_connection()
    cursor = conn.cursor()
    
    cursor = conn.execute("SELECT idusuario,       nombre,       numero,       correo,       contrasena  FROM usuario where nivel='C'")
    data=cursor.fetchall()
    cursor = conn.execute("SELECT idusuario,       nombre,       numero,       correo,       contrasena  FROM usuario where nivel='A'")
    data2=cursor.fetchall()
    conn.close()
    return render_template('administrarusuarios.html',username=user.usuar,cat=user.nivel,invent=data,invent2=data2)
        

#nuevo producto
@app.route('/nuevop', methods=["GET","POST"])
def nuevop():
    error=None
    conn = db_connection()
    cursor = conn.cursor()
    if request.method=='POST':
        
        idart=request.form.get("codigopro")
        
        nombre=request.form.get("nombrepro")
        descr=request.form.get("descripcion")
        precio=request.form.get("precio")
        marca=request.form.get("marca")
        categoria=request.form.get("categoria")
        cantidad=request.form.get("cantidad")
        
        image=request.files["imagen"]

         
        account=cursor.execute("select idinventario from inventario order by idinventario  desc")
        account = cursor.fetchone()
        conn.commit()
        idinvent=int(account[0])+1

        if idart=="" or nombre=="" or descr=="" or precio=="" or marca=="" or categoria=="" or cantidad=="" or image.filename=="":
            error= "Complete Todods Los espacios!"
            return render_template('productonuevo.html',username=user.usuar,cat=user.nivel, error=error)
        else:
           
           tuplainvent=(idinvent,cantidad) 
           cursor=conn.execute("INSERT INTO inventario ( idinventario, cantidadarat  ) VALUES ( ?,?)",tuplainvent)          
           image.save(image.filename)
           blob= convertToBinaryData(image.filename)
           tuplaprod=(idart,categoria,idinvent,nombre,descr,marca,precio, blob)
           cursor=conn.execute("INSERT INTO articulo ( idarticulo, idcategoria,  idinventario,    nombre,  descripcion,  marca,    precio,  imagen ) VALUES ( ?,?,?,?,?,?,?,?)",tuplaprod)          
           conn.commit()
           error="Guardado"
           return render_template('productonuevo.html',username=user.usuar,cat=user.nivel, error=error)
    
    if request.method =="GET":
        return  render_template("productonuevo.html",username=user.usuar,cat=user.nivel)

        
    

#index el inicio de todo
@app.route('/' )
def index():
    
    inventarioinicio()
    user= usuario(0,0,0,0,0,0,0)
    return render_template('index.html', producto0=tuplaproducto[0],producto1=tuplaproducto[1],producto2=tuplaproducto[2],producto3=tuplaproducto[3],producto4=tuplaproducto[4],producto5=tuplaproducto[5],precio0=tuplaprecios[0],precio1=tuplaprecios[1],precio2=tuplaprecios[2],precio3=tuplaprecios[3],precio4=tuplaprecios[4],precio5=tuplaprecios[5])

#pedido
@app.route('/<int:id>pedido', methods=["GET","POST"])
def pedido(id):
    #error : None
    conn = db_connection()
    cursor = conn.cursor()
    usu=user.idusaurio
    if  request.method=='POST':
        cantidad=request.form.get("cantidad")
        cursor=conn.execute("Select idpedido from pedido where idusuario= "+str(usu)+" and estado<>'V' and estado<>'C' order by idpedido desc")
        account=cursor.fetchone()
        if account:
            idpedi=account[0]
            artped=(idpedi,id,cantidad)
            cursor=conn.execute("INSERT INTO articulopedido ( idpedido,idarticulo, cantidad  ) VALUES ( ?,?,?)",artped)
            conn.commit()
            return redirect(url_for('listaprod',id=1))
        else:
            cursor=conn.execute("INSERT INTO pedido ( idusuario, estado  ) VALUES ( "+ str(usu)+",'N')")
            conn.commit()
            cursor=conn.execute("Select idpedido from pedido where idusuario= "+str(usu)+" and estado<>'V' and estado<>'C' order by idpedido desc")
            account=cursor.fetchone()
            idpedi=account[0]
            artped=(idpedi,id,cantidad)
            cursor=conn.execute("INSERT INTO articulopedido ( idpedido,idarticulo, cantidad  ) VALUES ( ?,?,?)",artped)
            conn.commit()
            return redirect(url_for('listaprod',id=1))
    
    if request.method =="GET":
        return  redirect(url_for('listaprod',id=1))



#para convertir de blob a img 
# poner en el html img src="data:image/png/jpeg;base64,{{ foto }}"
@app.route('/prueb')
def pru():
    imagen=None
    conn = db_connection()
    cursor = conn.cursor()
    cursor = conn.execute("SELECT  imagen  FROM articulo where idarticulo=1;")
    account = cursor.fetchone()
    
    imagen=account[0]
    beta=b64encode(imagen).decode("utf-8")
    return render_template('prueba.html', foto=beta)


app.run()