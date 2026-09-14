from flask import Flask, render_template, request, jsonify, session, redirect
from datetime import datetime, date
from functools import wraps
import uuid

app = Flask(__name__, template_folder='views', static_folder='static')
app.secret_key = 'media-luna-demo-secret-2026'

USERS = {
    'medialuna': {'password':'Medialuna2026','role':'Administrador'},
    'recepcionista01': {'password':'Recepcion2026','role':'Recepcionista'},
    'aseo01': {'password':'Aseo2026','role':'Personal de limpieza'},
}

PERMISSIONS = {
    'Administrador': {'inicio','clientes','habitaciones','reservas','hospedajes','inventario','facturacion','llamadas','equipaje','aseo','historial','empleados','administracion','auditoria'},
    'Recepcionista': {'inicio','clientes','habitaciones','reservas','hospedajes','llamadas','equipaje','aseo'},
    'Personal de limpieza': {'inicio','habitaciones','aseo'},
}

ROOM_TYPES = {
    'Sencilla': {'price':120000,'capacity':2,'beds':'1 cama','features':['Wi-Fi','TV','Aire acondicionado','Baño privado']},
    'Pareja': {'price':200000,'capacity':2,'beds':'1 cama doble','features':['Wi-Fi','TV','Aire acondicionado','Minibar']},
    'Familiar': {'price':350000,'capacity':4,'beds':'2 camas','features':['Wi-Fi','TV','Aire acondicionado','Minibar','Desayuno']},
    'Presidencial': {'price':300000,'capacity':4,'beds':'1 cama king','features':['Wi-Fi','TV','Aire acondicionado','Minibar','Sala privada','Jacuzzi']},
}

rooms=[]
for i in range(1,21):
    if i<=6: typ='Sencilla'
    elif i<=12: typ='Pareja'
    elif i<=17: typ='Familiar'
    else: typ='Presidencial'
    rooms.append({'id':str(100+i),'type':typ,'status':'Disponible','number':str(100+i),'features':ROOM_TYPES[typ]['features'], 'capacity':ROOM_TYPES[typ]['capacity'], 'price':ROOM_TYPES[typ]['price']})
rooms[1]['status']='Ocupada'; rooms[7]['status']='Reservada'; rooms[12]['status']='En proceso de aseo'; rooms[18]['status']='En proceso de facturación'; rooms[19]['status']='Suspendida'

customers=[
 {'id':'CLI-0001','name':'María González','document':'CC 52.456.789','nationality':'Colombiana','phone':'300 555 1010','email':'maria@email.com'},
 {'id':'CLI-0002','name':'Carlos Ramírez','document':'CC 79.456.123','nationality':'Colombiana','phone':'301 555 2020','email':'carlos@email.com'},
 {'id':'CLI-0003','name':'Ana López','document':'CC 43.987.654','nationality':'Colombiana','phone':'302 555 3030','email':'ana@email.com'},
 {'id':'CLI-0004','name':'Luis Torres','document':'Pasaporte PA123456','nationality':'Extranjera','phone':'303 555 4040','email':'luis@email.com'},
]
reservations=[
 {'id':'RES-00024','customer':'María González','rooms':['201'],'checkin':'2026-09-01','checkout':'2026-09-05','status':'Confirmada','origin':'Internet','guests':2},
 {'id':'RES-00023','customer':'Carlos Ramírez','rooms':['305','306'],'checkin':'2026-09-01','checkout':'2026-09-03','status':'Confirmada','origin':'Llamada','guests':4},
 {'id':'RES-00022','customer':'Ana López','rooms':['102'],'checkin':'2026-09-02','checkout':'2026-09-04','status':'Pendiente','origin':'Internet','guests':2},
 {'id':'RES-00021','customer':'Luis Torres','rooms':['403'],'checkin':'2026-09-03','checkout':'2026-09-05','status':'Confirmada','origin':'Internet','guests':2},
]
hospedajes=[]
cleaning=[
 {'id':'ASE-001','room':'112','employee':'aseo01','status':'Pendiente','priority':'Alta','task':'Limpieza completa','notes':''},
 {'id':'ASE-002','room':'113','employee':'aseo01','status':'En proceso','priority':'Media','task':'Limpieza completa','notes':''},
 {'id':'ASE-003','room':'114','employee':'aseo01','status':'Pendiente','priority':'Media','task':'Inspección','notes':''},
]
inventory=[
 {'id':'INV-001','name':'Toallas','category':'Habitaciones','stock':25,'min':10,'unit':'und'},
 {'id':'INV-002','name':'Jabón','category':'Aseo','stock':8,'min':10,'unit':'und'},
 {'id':'INV-003','name':'Agua botella','category':'Alimentos','stock':40,'min':15,'unit':'und'},
 {'id':'INV-004','name':'Botiquín','category':'Primeros auxilios','stock':6,'min':5,'unit':'und'},
]
inventory_moves=[]
luggage=[]; invoices=[]; calls=[]; employees=[
 {'id':'EMP-001','name':'Laura Martínez','role':'Recepcionista','status':'Activo'},
 {'id':'EMP-002','name':'Carlos Pérez','role':'Personal de limpieza','status':'Activo'},
 {'id':'EMP-003','name':'Andrea Gómez','role':'Administradora','status':'Activo'},
]
audit=[]

def audit_log(action, detail=''):
    user=session.get('user','Cliente público'); role=session.get('role','Público')
    now=datetime.now()
    audit.insert(0, {'user':user,'role':role,'action':action,'detail':detail,'date':now.strftime('%d/%m/%Y'),'time':now.strftime('%H:%M:%S')})
    del audit[100:]

def auth_required(f):
    @wraps(f)
    def w(*a,**kw):
        if not session.get('user'): return jsonify({'ok':False,'error':'No autenticado'}),401
        return f(*a,**kw)
    return w

def permission(module):
    def deco(f):
        @wraps(f)
        def w(*a,**kw):
            if not session.get('user'): return jsonify({'ok':False,'error':'No autenticado'}),401
            if module not in PERMISSIONS.get(session.get('role'),set()): return jsonify({'ok':False,'error':'Sin permisos'}),403
            return f(*a,**kw)
        return w
    return deco

def rid(prefix): return f'{prefix}-{uuid.uuid4().hex[:6].upper()}'

@app.get('/')
def home():
    return render_template('index.html')

@app.get('/login')
def login():
    if session.get('user'): return redirect('/app')
    return render_template('login.html')

@app.get('/app')
def app_view():
    if not session.get('user'): return redirect('/login')
    return render_template('app.html', user=session['user'], role=session['role'], permissions=list(PERMISSIONS[session['role']]))

@app.get('/publico')
def public(): return render_template('index.html')

@app.post('/api/login')
def api_login():
    d=request.get_json() or {}; u=d.get('user','').strip(); p=d.get('password','')
    item=USERS.get(u)
    if not item or item['password']!=p: return jsonify({'ok':False,'error':'Usuario o contraseña incorrectos'}),401
    session['user']=u; session['role']=item['role']; audit_log('Inicio de sesión','Acceso al sistema')
    return jsonify({'ok':True,'user':u,'role':item['role']})

@app.post('/api/logout')
def logout(): audit_log('Cierre de sesión','El usuario cerró la sesión'); session.clear(); return jsonify({'ok':True})

@app.get('/api/state')
@auth_required
def state():
    return jsonify({'user':session['user'],'role':session['role'],'rooms':rooms,'customers':customers,'reservations':reservations,'hospedajes':hospedajes,'cleaning':cleaning,'inventory':inventory,'luggage':luggage,'invoices':invoices,'calls':calls,'employees':employees,'audit':audit,'permissions':list(PERMISSIONS[session['role']])})

@app.post('/api/customers')
@permission('clientes')
def add_customer():
    d=request.get_json() or {}; c={'id':rid('CLI'),'name':d.get('name',''),'document':d.get('document',''),'nationality':d.get('nationality',''),'phone':d.get('phone',''),'email':d.get('email','')}
    if not c['name'] or not c['document']: return jsonify({'ok':False,'error':'Nombre y documento son obligatorios'}),400
    customers.insert(0,c); audit_log('Registrar cliente',c['name']); return jsonify({'ok':True,'item':c})

@app.post('/api/rooms')
@permission('habitaciones')
def add_room():
    d=request.get_json() or {}; typ=d.get('type','Sencilla')
    if typ not in ROOM_TYPES: return jsonify({'ok':False,'error':'Tipo inválido'}),400
    num=d.get('number','').strip()
    if not num: return jsonify({'ok':False,'error':'Número obligatorio'}),400
    r={'id':num,'number':num,'type':typ,'status':d.get('status','Disponible'),'capacity':ROOM_TYPES[typ]['capacity'],'price':ROOM_TYPES[typ]['price'],'features':ROOM_TYPES[typ]['features']}
    rooms.insert(0,r); audit_log('Registrar habitación',f'Habitación {num}'); return jsonify({'ok':True,'item':r})

@app.patch('/api/rooms/<room_id>')
@permission('habitaciones')
def edit_room(room_id):
    d=request.get_json() or {}; r=next((x for x in rooms if x['id']==room_id),None)
    if not r:return jsonify({'ok':False,'error':'Habitación no encontrada'}),404
    if d.get('type') in ROOM_TYPES:
        r['type']=d['type']; r['price']=ROOM_TYPES[d['type']]['price']; r['capacity']=ROOM_TYPES[d['type']]['capacity']; r['features']=ROOM_TYPES[d['type']]['features']
    if d.get('status'): r['status']=d['status']
    audit_log('Modificar habitación',room_id); return jsonify({'ok':True,'item':r})

@app.post('/api/reservations')
def add_reservation():
    d=request.get_json() or {}; selected=d.get('rooms') or []
    if not d.get('name') or not d.get('checkin') or not d.get('checkout') or not selected: return jsonify({'ok':False,'error':'Completa datos, fechas y al menos una habitación'}),400
    available=[r for r in rooms if r['id'] in selected and r['status']=='Disponible']
    if len(available)!=len(selected): return jsonify({'ok':False,'error':'Una o más habitaciones no están disponibles'}),400
    c=next((x for x in customers if x['document']==d.get('document')),None)
    if not c:
        c={'id':rid('CLI'),'name':d['name'],'document':d.get('document','Pendiente'),'nationality':d.get('nationality',''),'phone':d.get('phone',''),'email':d.get('email','')}; customers.insert(0,c)
    r={'id':rid('RES'),'customer':d['name'],'rooms':selected,'checkin':d['checkin'],'checkout':d['checkout'],'status':'Pendiente','origin':d.get('origin','Internet'),'guests':int(d.get('guests',1))}
    reservations.insert(0,r)
    for room in available: room['status']='Reservada'
    audit_log('Registrar reserva',f"{r['id']} · {r['origin']}")
    return jsonify({'ok':True,'item':r})

@app.patch('/api/reservations/<res_id>')
@permission('reservas')
def reservation_action(res_id):
    d=request.get_json() or {}; r=next((x for x in reservations if x['id']==res_id),None)
    if not r:return jsonify({'ok':False,'error':'Reserva no encontrada'}),404
    action=d.get('action')
    if action=='confirm': r['status']='Confirmada'
    elif action=='cancel':
        r['status']='Cancelada'
        for room in rooms:
            if room['id'] in r['rooms']: room['status']='Disponible'
    elif action=='checkin':
        r['status']='En hospedaje'
        for room in rooms:
            if room['id'] in r['rooms']: room['status']='Ocupada'
        hospedajes.insert(0,{'id':rid('HOS'),'reservation':r['id'],'customer':r['customer'],'rooms':r['rooms'],'checkin':r['checkin'],'checkout':r['checkout'],'status':'Activo','actual_checkin':datetime.now().strftime('%Y-%m-%d %H:%M')})
    elif action=='checkout':
        r['status']='Finalizada'
        for room in rooms:
            if room['id'] in r['rooms']: room['status']='En proceso de aseo'
        h=next((x for x in hospedajes if x['reservation']==r['id'] and x['status']=='Activo'),None)
        if h: h['status']='Finalizado'; h['actual_checkout']=datetime.now().strftime('%Y-%m-%d %H:%M')
    else:return jsonify({'ok':False,'error':'Acción inválida'}),400
    audit_log(f"Reserva {action}",res_id); return jsonify({'ok':True,'item':r})

@app.post('/api/cleaning')
@permission('aseo')
def add_cleaning():
    d=request.get_json() or {}; item={'id':rid('ASE'),'room':d.get('room',''),'employee':d.get('employee','aseo01'),'status':'Pendiente','priority':d.get('priority','Media'),'task':d.get('task','Limpieza completa'),'notes':d.get('notes','')}
    if not item['room']: return jsonify({'ok':False,'error':'Habitación obligatoria'}),400
    cleaning.insert(0,item); rr=next((x for x in rooms if x['id']==item['room']),None)
    if rr: rr['status']='En proceso de aseo'
    audit_log('Crear tarea de limpieza',item['room']); return jsonify({'ok':True,'item':item})

@app.patch('/api/cleaning/<cid>')
@permission('aseo')
def cleaning_action(cid):
    d=request.get_json() or {}; item=next((x for x in cleaning if x['id']==cid),None)
    if not item:return jsonify({'ok':False,'error':'Tarea no encontrada'}),404
    item['status']='En proceso' if d.get('action')=='start' else ('Completada' if d.get('action')=='complete' else item['status'])
    if item['status']=='Completada':
        rr=next((x for x in rooms if x['id']==item['room']),None)
        if rr: rr['status']='Disponible'
    audit_log('Actualizar limpieza',f"{item['room']} · {item['status']}"); return jsonify({'ok':True,'item':item})

@app.post('/api/inventory/movement')
@permission('inventario')
def inventory_move():
    d=request.get_json() or {}; item=next((x for x in inventory if x['id']==d.get('product')),None); qty=int(d.get('quantity',0) or 0); typ=d.get('type')
    if not item or qty<=0 or typ not in ('Entrada','Consumo','Pérdida / Daño'): return jsonify({'ok':False,'error':'Movimiento inválido'}),400
    if typ=='Entrada': item['stock']+=qty
    else: item['stock']=max(0,item['stock']-qty)
    mv={'id':rid('MOV'),'product':item['name'],'type':typ,'quantity':qty,'user':session['user'],'date':datetime.now().strftime('%d/%m/%Y'),'time':datetime.now().strftime('%H:%M:%S')}; inventory_moves.insert(0,mv); audit_log('Movimiento de inventario',f"{item['name']} · {typ} · {qty}"); return jsonify({'ok':True,'item':mv,'inventory':item})

@app.post('/api/luggage')
@permission('equipaje')
def add_luggage():
    d=request.get_json() or {}; item={'id':rid('EQU'),'guest':d.get('guest',''),'room':d.get('room',''),'status':d.get('status','Buen estado'),'observations':d.get('observations',''),'registered':datetime.now().strftime('%d/%m/%Y %H:%M')}; luggage.insert(0,item); audit_log('Registrar equipaje',item['guest']); return jsonify({'ok':True,'item':item})

@app.post('/api/invoices')
@permission('facturacion')
def add_invoice():
    d=request.get_json() or {}; qty=int(d.get('quantity',1) or 1); price=int(d.get('price',0) or 0); item={'id':rid('FAC'),'customer':d.get('customer',''),'concept':d.get('concept','Hospedaje'),'quantity':qty,'price':price,'total':qty*price,'electronic_status':'Pendiente de integración DIAN','date':datetime.now().strftime('%d/%m/%Y')}; invoices.insert(0,item); audit_log('Generar factura',item['id']); return jsonify({'ok':True,'item':item})

@app.post('/api/calls')
@permission('llamadas')
def add_call():
    d=request.get_json() or {}; item={'id':rid('LLA'),'phone':d.get('phone',''),'client':d.get('client',''),'subject':d.get('subject',''),'notes':d.get('notes',''),'user':session['user'],'date':datetime.now().strftime('%d/%m/%Y %H:%M')}; calls.insert(0,item); audit_log('Registrar llamada',item['subject']); return jsonify({'ok':True,'item':item})

@app.post('/api/employees')
@permission('empleados')
def add_employee():
    d=request.get_json() or {}; item={'id':rid('EMP'),'name':d.get('name',''),'role':d.get('role','Recepcionista'),'status':'Activo'}; employees.insert(0,item); audit_log('Registrar empleado',item['name']); return jsonify({'ok':True,'item':item})

@app.delete('/api/audit')
@permission('auditoria')
def clear_audit(): audit.clear(); return jsonify({'ok':True})

@app.get('/api/public/rooms')
def public_rooms(): return jsonify([r for r in rooms if r['status']=='Disponible'])

if __name__=='__main__': app.run(debug=True, host='127.0.0.1', port=8000)
