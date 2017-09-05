
# coding: utf-8
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from rest_framework.test import APITestCase
import models
import json
import pprint
import serializers

class APIUsuariosTests(APITestCase):

    def setUp(self):
        #escuela = models.Escuela.objects.create(nombre="Escuela de ejemplo", cue="123")
        #escuela.save()
        pass

    def test_ruta_principal_de_la_api(self):
        response = self.client.get('/api/', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['users'], "http://testserver/api/users", "Debería entregar la URL para acceder a usuarios.")

    def test_ruta_users(self):
        response = self.client.get('/api/users', format='json')
        self.assertNotEquals(response, None)

    def test_ruta_escuelas(self):
        response = self.client.get('/api/escuelas', format='json')
        self.assertEquals(response.data['results'], [], "Inicialmente no hay escuelas cargadas")

        # Se genera una escuela de prueba.
        escuela = models.Escuela.objects.create(nombre="Escuela de ejemplo", cue="123")
        escuela.save()

        # ahora la API tiene que exponer una sola escuela.
        response = self.client.get('/api/escuelas', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 1, "Tiene que retornarse un solo registro")


class GeneralesTestCase(APITestCase):

    def test_pagina_principal_retorna_ok(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_puede_pedir_agenda_administrador(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se genera un grupo
        grupo = Group.objects.create(name="Administrador")

        # Se genera un usuario demo
        user_2 = User.objects.create_user(username='demo', password='123')
        user_2.perfil.group = grupo
        user_2.perfil.save()

        # Se genera 1 escuela
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        escuela_1 = models.Escuela.objects.create(cue="1", nombre="Escuela 1", localidad=localidad_1)

        # Se crea una categoria
        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria 1")

        # Se crean dos eventos de prueba. Uno con fecha Enero y otro Marzo
        evento_1 = models.Evento.objects.create(titulo="Evento de prueba", categoria=categoria_1, responsable=user_2.perfil, escuela=escuela_1, fecha="2017-01-15", fecha_fin="2017-01-15")
        evento_2 = models.Evento.objects.create(titulo="Evento de prueba de Marzo", categoria=categoria_1, responsable=user_2.perfil, escuela=escuela_1, fecha="2017-03-15", fecha_fin="2017-03-15")

        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&perfil=2&region=1', format='json')

        self.assertEqual(response.data['cantidad'], 1)
        self.assertEqual(len(response.data['eventos']), 1)

    def test_puede_pedir_agenda_coordinador(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se genera un grupo
        grupo = Group.objects.create(name="Coordinador")

        # Se crean dos regiones
        region_1 = models.Region.objects.create(numero=1)
        region_23 = models.Region.objects.create(numero=23)

        # Se crea dos distritos
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        distrito_2 = models.Distrito.objects.create(nombre="distrito2", region=region_23)

        # Se crea una localidad
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        localidad_2 = models.Localidad.objects.create(nombre="localidad2", distrito=distrito_2)

        # Se genera un usuario demo, se asigna una region al perfil
        user_2 = User.objects.create_user(username='demo', password='123')
        perfil_2 = user_2.perfil
        perfil_2.region = region_1
        perfil_2.group = grupo
        perfil_2.save()

        # Se generan 2 escuela y se les asigna distinta localidad
        escuela_1 = models.Escuela.objects.create(cue="1", nombre="escuela 1", localidad=localidad_1)
        escuela_2 = models.Escuela.objects.create(cue="2", nombre="escuela 2", localidad = localidad_2)


        # Se crea una categoria
        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria 1")

        # Se crean eventos de prueba con fecha de Enero.
        evento_1 = models.Evento.objects.create(
            titulo="Evento de prueba de region 1 y Responsable perfil 2",
            categoria=categoria_1,
            responsable=user_2.perfil,
            escuela=escuela_1,
            fecha="2017-01-15",
            fecha_fin="2017-01-15")
        evento_2 = models.Evento.objects.create(
            titulo="Otro evento de prueba de otra escuela, de otra region, de perfil 2",
            categoria=categoria_1,
            responsable=user_2.perfil,
            escuela=escuela_2,
            fecha="2017-01-25",
            fecha_fin="2017-01-25")
        evento_3 = models.Evento.objects.create(
            titulo="Evento de otro perfil, pero de region 1",
            categoria=categoria_1,
            responsable=user.perfil,
            escuela=escuela_1,
            fecha="2017-01-25",
            fecha_fin="2017-01-25")

        # Pide todos (Caso Administrador, Administración y Referente)
        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01', format='json')

        self.assertEqual(response.data['cantidad'], 3)

        # Pide solo los de región 1 (Caso Coordinador)
        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&region=1', format='json')

        self.assertEqual(response.data['cantidad'], 2)

        # Pide solo región 23 (Caso Coordinador)
        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&region=23', format='json')

        self.assertEqual(response.data['cantidad'], 1)

        # Pide solo perfil 2 (Caso Facilitador ) y Región 1
        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&perfil=2&region=1', format='json')

        self.assertEqual(response.data['cantidad'], 1)

    def test_puede_crear_escuela(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se crean 1 localidad, 1 distrito y 1 región
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)

        # Se crea un area Urbana
        area = models.Area.objects.create(nombre="Urbana")

        # Se crea una modalidad
        modalidad = models.Modalidad.objects.create(nombre="Especial")

        # Se crea un nivel
        nivel = models.Nivel.objects.create(nombre="Primaria")

        # Se crea un piso
        piso = models.Piso.objects.create(servidor="Servidor EXO")

        # Se crea un tipo de financiamiento
        tipo_de_financiamiento = models.TipoDeFinanciamiento.objects.create(nombre="Provincial")

        #Se crea un tipo de gestión
        tipo_de_gestion = models.TipoDeGestion.objects.create(nombre="Privada")

        data = {
            "data": {
                "type": "escuelas",
                "attributes": {
                    "cue": "88008800",
                    "nombre": "Escuela de Prueba desde el test",
                },
                'relationships': {
                    "area": {
                        "data": {
                            "type": "areas",
                            "id": area.id,
                        },
                    },
                    "localidad": {
                        "data": {
                            "type": "localidades",
                            "id": localidad_1.id
                        }
                    },
                    "modalidad": {
                        "data": {
                            "type": "modalidades",
                            "id": modalidad.id
                        }
                    },
                    "nivel": {
                        "data": {
                            "type": "niveles",
                            "id": nivel.id
                        }
                    },
                    #"motivo_de_conformacion": None,
                    #"padre": None,
                    "piso": {
                        "data": {
                            "type": "pisos",
                            "id": piso.id
                        }
                    },
                    "tipo_de_financiamiento": {
                        "data": {
                            "type": "tipos-de-financiamiento",
                            "id": tipo_de_financiamiento.id,
                        }
                    },
                    "tipo_de_gestion": {
                        "data": {
                            "type": "tipos-de-gestion",
                            "id": tipo_de_gestion.id
                        }
                    }
                }
                # "direccion": "",
                # "telefono": "",
                # "email": "",
                # "latitud": "",
                # "longitud": "",
                # "fecha-conformacion": null,
                # "estado": false,
                # "conformada": false
            }
        }

        # Inicialmente no hay ninguna escuela
        self.assertEqual(models.Escuela.objects.all().count(), 0)

        # Luego de hacer el post ...
        post = self.client.post('/api/escuelas', json.dumps(data), content_type='application/vnd.api+json')

        # Luego tiene que haber una escuela
        self.assertEqual(models.Escuela.objects.all().count(), 1)

        # Y la api tiene que retornarla
        response = self.client.get('/api/escuelas/1')
        self.assertEqual(response.data['cue'], '88008800')
        self.assertEqual(response.data['nombre'], 'Escuela de Prueba desde el test')

    def test_puede_conformar_escuelas(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        motivo = models.MotivoDeConformacion.objects.create(nombre="Prueba")

        # Se generan 3 escuelas
        escuela_1 = models.Escuela.objects.create(cue="1")
        escuela_2 = models.Escuela.objects.create(cue="2")
        escuela_3 = models.Escuela.objects.create(cue="3")

        # Inicialmente las 3 escuelas son de primer nivel, se retornan en /api/escuelas
        response = self.client.get('/api/escuelas', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 3)

        # Realizando una conformación. Escuela 1 va a absorver a escuela_2
        escuela_1.conformar_con(escuela_2, motivo)

        # Ahora la api tiene que retornar solo 2 escuelas
        response = self.client.get('/api/escuelas?conformada=false', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 2)

        # Se realiza una conformación más, la 1 absorbe a la 3.
        escuela_1.conformar_con(escuela_3, motivo)
        self.assertEqual(escuela_1.subescuelas.count(), 2)

        self.assertTrue(escuela_3.conformada)

        # Ahora la api tiene que retornar solo 1 escuela
        response = self.client.get('/api/escuelas?conformada=false', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 1)

        # No debería permitirse conformar una escuela más de una vez.
        with self.assertRaises(AssertionError):
            escuela_1.conformar_con(escuela_3, motivo)

        # Ni una escuela con sigo misma
        with self.assertRaises(AssertionError):
            escuela_1.conformar_con(escuela_1, motivo)

        # Ni una escuela que ya se conformó

        """
        # Deshabilitado temporalmente, porque el importador no realiza las
        # conformaciones en orden.

        with self.assertRaises(AssertionError):
            escuela_3.conformar_con(escuela_1, motivo)
        """


        # Por último, la conformación se tiene que poder hacer desde la API
        escuela_4 = models.Escuela.objects.create(cue="4")

        # Inicialmente no está conformada
        self.assertFalse(escuela_4.conformada)

        data = {
            'escuela_que_se_absorbera': escuela_4.id,
            'motivo_id': motivo.id
        }

        response = self.client.post('/api/escuelas/%d/conformar' %(escuela_1.id), data)

        # NOTA: Luego de hacer el request, se tiene que actualizar el objeto
        escuela_4 = models.Escuela.objects.get(id=4)

        self.assertEqual(escuela_4.padre, escuela_1)
        self.assertTrue(escuela_4.motivo_de_conformacion, 'tiene que tener un motivo')
        self.assertTrue(escuela_4.fecha_conformacion, 'tiene que tener una fecha')

        # La escuela 4 se conformó, la api tiene que informarlo
        response = self.client.get('/api/escuelas/4', format='json')
        self.assertEqual(response.data['conformada'], True)

        # La escuela 1 nunca se conformó
        response = self.client.get('/api/escuelas/1', format='json')
        self.assertEqual(response.data['conformada'], False)

        self.assertEqual(escuela_1.subescuelas.count(), 3)

        # Y las estadisticas funcionan filtrando conformadas.
        response = self.client.get('/api/escuelas/estadistica', format='json')
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['abiertas'], 1)
        self.assertEqual(response.data['conformadas'], 3)


class Permisos(APITestCase):

    def test_puede_serializar_permisos(self):
        # Comienza con un usuario básico
        user = User.objects.create_user(username='test', password='123')

        # Se genera un grupo Coordinador, con un permiso
        grupo = Group.objects.create(name='coordinador')

        tipo = ContentType.objects.get(app_label='escuelas', model='evento')

        puede_crear = Permission(name='evento.crear', codename='evento.crear', content_type=tipo)
        puede_crear.save()

        puede_listar = Permission(name='evento.listar', codename='evento.listar', content_type=tipo)
        puede_listar.save()

        puede_administrar = Permission(name='evento.administrar', codename='evento.administrar', content_type=tipo)
        puede_administrar.save()

        # El grupo tiene un solo permiso
        grupo.permissions.add(puede_crear)

        # Se agrega al usuario a ese grupo coordinador
        user.perfil.group = grupo

        # Se asigna una region al perfil de usuario
        region_1 = models.Region.objects.create(numero=1)
        user.perfil.region = region_1

        grupo.save()
        user.save()
        user.perfil.save()

        # En este punto, tiene que existir un perfil de usuario que puede
        # retornar la lista de permisos a traves de la api.
        self.client.login(username='test', password='123')

        # Forzando autenticación porque sin sessionStore de configuración
        # la llamada a self.client.login no guarda la autenticación para las
        # siguientes llamadas.
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/mi-perfil', format='json')

        self.assertEqual(response.data['username'], "test");
        self.assertEqual(len(response.data['grupos']), 1, "Tiene un solo grupo")
        self.assertEqual(response.data['grupos'][0]['nombre'], 'coordinador', "Tiene asignado el grupo coordinador")

        # Hay 3 permisos en el sistema en total
        self.assertEqual(len(response.data['permisos']), 3)

        # Pero esta es la asignación, el usuario de este grupo solo puede crear eventos:
        self.assertEqual(response.data['permisos']['evento.crear'], True);
        self.assertEqual(response.data['permisos']['evento.listar'], False);
        self.assertEqual(response.data['permisos']['evento.administrar'], False);

        response = self.client.get('/api/mi-perfil/1/detalle', format='json')

        # En la vista detalle del grupo ocurre lo mismo, se ven 3 permisos pero este grupo
        # solo puede crear eventos.
        self.assertEqual(response.data['permisos']['evento.crear'], True);
        self.assertEqual(response.data['permisos']['evento.listar'], False);
        self.assertEqual(response.data['permisos']['evento.administrar'], False);

        self.assertEqual(len(response.data['permisosAgrupados']), 1);
        self.assertEqual(response.data['permisosAgrupados'][0]['modulo'], 'evento');
        self.assertEqual(len(response.data['permisosAgrupados'][0]['permisos']), 3);

        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][0]['accion'], 'crear');
        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][0]['permiso'], True);

        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][1]['accion'], 'administrar');
        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][1]['permiso'], False);

        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][2]['accion'], 'listar');
        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][2]['permiso'], False);


    def test_puede_obtener_una_lista_de_todos_los_permisos(self):
        user = User.objects.create_user(username='test', password='123')

        grupo = Group.objects.create(name='coordinador')
        tipo = ContentType.objects.get(app_label='escuelas', model='evento')
        puede_crear_eventos = Permission(name='crear', codename='evento.crear', content_type=tipo)
        puede_crear_eventos.save()

        grupo.permissions.add(puede_crear_eventos)

        self.client.force_authenticate(user=user)
        response = self.client.get('/api/permissions', format='json')

        self.assertEqual(len(response.data['results']), 1)
        item_1 = response.data['results'][0]
        self.assertEquals(item_1["name"], "crear")
        self.assertEquals(item_1["codename"], "evento.crear")
        self.assertEquals(item_1["content_type"], "evento")

    def test_puede_obtener_grupos_junto_con_permisos(self):
        user = User.objects.create_user(username='test', password='123')

        grupo = Group.objects.create(name='coordinador')
        tipo = ContentType.objects.get(app_label='escuelas', model='evento')
        puede_crear_eventos = Permission(name='crear', codename='evento.crear', content_type=tipo)
        puede_crear_eventos.save()

        grupo.permissions.add(puede_crear_eventos)

        self.client.force_authenticate(user=user)
        response = self.client.get('/api/groups', format='json')

        self.assertEqual(len(response.data['results']), 1)
        item_1 = response.data['results'][0]

        self.assertEquals(item_1["name"], "coordinador")

        # Inicialmente este grupo no tiene perfil
        self.assertEquals(item_1["perfiles"], [])

        # Si se vincula el grupo a un perfil ...
        user.perfil.group = grupo
        grupo.save()
        user.save()
        user.perfil.save()

        response = self.client.get('/api/groups', format='json')
        item_1 = response.data['results'][0]

        self.assertEquals(len(item_1["perfiles"]), 1)
        self.assertEquals(item_1["perfiles"][0]['type'], 'perfiles')


class Filtar(APITestCase):

    def test_puede_filtrar_perfiles(self):
        # Comienza con un usuario básico
        user = User.objects.create_user(username='test', password='123')
        user2 = User.objects.create_user(username='hugo', password='123')

        user.save()
        user.perfil.nombre = "test"
        user.perfil.save()

        user2.save()
        user2.perfil.nombre = "hugo"
        user2.perfil.save()

        # En este punto, tiene que existir un perfil de usuario que puede
        # retornar la lista de permisos a traves de la api.
        self.client.login(username='test', password='123')

        # Forzando autenticación porque sin sessionStore de configuración
        # la llamada a self.client.login no guarda la autenticación para las
        # siguientes llamadas.
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/perfiles', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 2);

        response = self.client.get('/api/perfiles?search=hugo', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 1);
