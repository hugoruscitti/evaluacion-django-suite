# coding: utf-8
from __future__ import unicode_literals
import datetime
import base64
import os
import subprocess
import uuid

import xlwt
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from escuelas import models, serializers


class EventoDeRoboticaViewSet(viewsets.ModelViewSet):
    resource_name = 'eventos-de-robotica'
    queryset = models.EventoDeRobotica.objects.all()
    serializer_class = serializers.EventoDeRoboticaSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['escuela__nombre', 'escuela__cue']
    filter_fields = ['escuela__localidad', 'escuela__localidad__distrito', "tallerista__id"]
    ordering_fields = ['fecha', 'escuela_id', 'escuela__localidad__distrito__region__numero', 'distrito', 'tallerista', 'fecha_de_creacion']

    def get_queryset(self):
        queryset = self.queryset
        query = self.request.query_params.get('query', None)

        filtro_desde = self.request.query_params.get('desde', None)
        filtro_hasta = self.request.query_params.get('hasta', None)
        filtro_desde_creacion = self.request.query_params.get('desde_creacion', None)
        filtro_hasta_creacion = self.request.query_params.get('hasta_creacion', None)
        filtro_region = self.request.query_params.get('escuela__localidad__distrito__region__numero', None)
        filtro_perfil = self.request.query_params.get('perfil', None)

        if filtro_desde:
            filtro = Q(fecha__gte=filtro_desde)
            queryset = queryset.filter(filtro)

        if filtro_hasta:
            filtro = Q(fecha__lte=filtro_hasta)
            queryset = queryset.filter(filtro)

        if filtro_desde_creacion:
            fecha = datetime.datetime.strptime(filtro_desde_creacion, "%Y-%m-%d")
            fecha = self.corregir_para_usar_timezone(fecha)

            filtro = Q(fecha_de_creacion__gte=fecha)
            queryset = queryset.filter(filtro)

        if filtro_hasta_creacion:
            fecha = datetime.datetime.strptime(filtro_hasta_creacion, "%Y-%m-%d")
            fecha += timedelta(days=1)

            fecha = self.corregir_para_usar_timezone(fecha)
            filtro = Q(fecha_de_creacion__lte=fecha)
            queryset = queryset.filter(filtro)

        if filtro_perfil:
            usuario = models.Perfil.objects.get(id=filtro_perfil)
            filtro = Q(tallerista=usuario)
            queryset = queryset.filter(filtro)
        else:
            if filtro_region:
                filtro = Q(escuela__localidad__distrito__region__numero=filtro_region)
                queryset = queryset.filter(filtro)

        if query:
            filtro_escuela = Q(escuela__nombre__icontains=query)
            filtro_escuela_cue = Q(escuela__cue__icontains=query)

            queryset = queryset.filter(filtro_escuela | filtro_escuela_cue)

        return queryset.distinct()

    def corregir_para_usar_timezone(self, fecha):
        default_timezone = timezone.get_default_timezone()
        return timezone.make_aware(fecha, default_timezone)

    def perform_update(self, serializer):
        return self.guardar_modelo_teniendo_en_cuenta_el_acta(serializer)

    def perform_create(self, serializer):
        return self.guardar_modelo_teniendo_en_cuenta_el_acta(serializer)

    def guardar_modelo_teniendo_en_cuenta_el_acta(self, serializer):
        instancia = serializer.save()
        acta = self.request.data.get('acta', None)

        # El acta llega desde el front-end como una lista de diccionarios,
        # donde cada diccionario representa un archivo, con nombre y contenido
        # en base 64.
        if acta and isinstance(acta, list):
            lista_de_archivos_temporales = []

            # Todos los archivos presentes en el front se convierten en archivos
            # físicos reales en /tmp.
            #
            # Este bucle que se encarga de generar todos esos archivos, y guardar
            # en lista_de_archivos_temporales todos los nombres de archivos
            # generados.
            for a in acta:
                nombre = a['name']
                contenido = a['contenido']

                archivo_temporal = self.guardar_archivo_temporal(nombre, contenido)
                lista_de_archivos_temporales.append(archivo_temporal)

            # Con la lista de archivos generados, se invoca a convert para generar
            # el archivo pdf con todas las imágenes.
            prefijo_aleatorio = str(uuid.uuid4())[:12]
            nombre_del_archivo_pdf = '/tmp/%s_archivo.pdf' %(prefijo_aleatorio)

            comando_a_ejecutar = ["convert"] + lista_de_archivos_temporales + ['-compress', 'jpeg', '-quality', '50', '-resize', '1024x1024', nombre_del_archivo_pdf]
            fallo = subprocess.call(comando_a_ejecutar)

            # Con el archivo pdf generado, se intenta cargar el campo 'acta' del
            # modelo django.
            if not fallo:
                from django.core.files import File
                reopen = open(nombre_del_archivo_pdf, "rb")
                django_file = File(reopen)

                instancia.acta.save('acta.pdf', django_file, save=False)
            else:
                raise Exception(u"Falló la generación del archivo pdf")

        instancia.save()
        return instancia

    def guardar_archivo_temporal(self, nombre, data):
        if 'data:' in data and ';base64,' in data:
            header, data = data.split(';base64,')

        decoded_file = base64.b64decode(data)
        complete_file_name = str(uuid.uuid4())[:12]+ "_" + nombre
        ruta_completa = os.path.join('/tmp', complete_file_name)

        filehandler = open(ruta_completa, "wb")
        filehandler.write(decoded_file)
        filehandler.close()

        return ruta_completa

    @list_route(methods=['get'])
    def informe(self, request):
        start_date = self.request.query_params.get('inicio', None)
        dni = self.request.query_params.get('dni', None)
        end_date = self.request.query_params.get('fin', None)
        filtro_tallerista = Q(tallerista__dni=dni)

        result = models.EventoDeRobotica.objects.filter(filtro_tallerista, fecha__range=(start_date, end_date))
        return Response({})

    @list_route(methods=['get'])
    def agenda(self, request):
        inicio = self.request.query_params.get('inicio', None)
        fin = self.request.query_params.get('fin', None)
        perfil = self.request.query_params.get('perfil', None)
        region = self.request.query_params.get('region', None)

        eventos = models.EventoDeRobotica.objects.filter(fecha__range=(inicio, fin))

        if region:
            eventos = eventos.filter(Q(escuela__localidad__distrito__region__numero=region) | Q(escuela__cue=60000000))

        if perfil:
            usuario = models.Perfil.objects.get(id=perfil) # El usuario logeado
            eventos = eventos.filter(Q(tallerista=usuario)).distinct()
            eventos = eventos[:]
        else:
            if region:
                eventos = [evento for evento in eventos if evento.esDelEquipoRegion(region)]
            else:
                eventos = eventos[:]


        return Response({
                "inicio": inicio,
                "fin": fin,
                "cantidad": len(eventos),
                "eventos": serializers.EventoDeRoboticaSerializer(eventos, many=True).data
            })

    @list_route(methods=['get'])
    def agenda_region(self, request):
        inicio = self.request.query_params.get('inicio', None)
        fin = self.request.query_params.get('fin', None)
        perfil = self.request.query_params.get('perfil', None)

        persona = models.Perfil.objects.get(id=perfil)
        region = persona.region.numero

        eventos = models.EventoDeRobotica.objects.filter( fecha__range=(inicio, fin), escuela__localidad__distrito__region__numero=region, tallerista=persona)
        return Response({
                "inicio": inicio,
                "fin": fin,
                "perfil": perfil,
                "persona": persona.apellido,
                "region_del_perfil": persona.region.numero,
                "cantidad": eventos.count(),
                "eventos": serializers.EventoDeRoboticaSerializer(eventos, many=True).data,
                "region": region
            })

    @list_route(methods=['get'])
    def estadistica(self, request):
        inicio = self.request.query_params.get('inicio', None)
        fin = self.request.query_params.get('fin', None)
        perfil = self.request.query_params.get('perfil', None)
        region = self.request.query_params.get('region', None)

        # eventos = models.EventoDeRobotica.objects.filter(fecha__range=(inicio, fin))
        eventos = models.EventoDeRobotica.objects.all()

        if region:
            eventos = eventos.filter(escuela__localidad__distrito__region__numero=region)

        if perfil:
            usuario = models.Perfil.objects.get(id=perfil) # El usuario logeado
            eventos = eventos.filter(Q(tallerista=usuario) | Q(acompaniantes=usuario)).distinct()

        total = eventos.count()
        conActaNueva = eventos.filter(acta__gt='').count()
        conActa = conActaNueva
        sinActa = total - conActa

        totalDeTalleres = models.EventoDeRobotica.objects.all().exclude(escuela__localidad__distrito__region__numero=None)
        region1 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=1)
        region2 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=2)
        region3 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=3)
        region4 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=4)
        region5 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=5)
        region6 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=6)
        region7 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=7)
        region8 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=8)
        region9 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=9)
        region10 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=10)
        region11= models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=11)
        region12 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=12)
        region13 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=13)
        region14 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=14)
        region15 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=15)
        region16 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=16)
        region17 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=17)
        region18 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=18)
        region19 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=19)
        region20 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=20)
        region21 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=21)
        region22 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=22)
        region23 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=23)
        region24 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=24)
        region25 = models.EventoDeRobotica.objects.filter(escuela__localidad__distrito__region__numero=25)

        estadisticas = {
            "totales": [
                {
                    "name": "Total",
                    "count": total,
                    "porcentaje": 100
                },
            ],
            "estado": [
                {
                    "name": "Finalizados",
                    "count": conActa,
                    "porcentaje": round(((conActa * 100.00) / total),2)
                },
                {
                    "name": "Abiertos",
                    "count": sinActa,
                    "porcentaje": round(((sinActa * 100.00) / total),2)
                }
            ],
            # "region1": [
            #     {
            #         "name": "Finalizados",
            #         "count": region1.filter(cerrar_evento=False).count(),
            #         "porcentaje": round((((region1.filter(cerrar_evento=False).count()) * 100.00) / region1.count()),2)
            #     },
            #     {
            #         "name": "Abiertos",
            #         "count": region1.filter(cerrar_evento=True).count(),
            #         "porcentaje": round((((region1.filter(cerrar_evento=True).count()) * 100.00) / region1.count()),2)
            #     }
            # ],
            # "region2": [
            #     {
            #         "name": "Finalizados",
            #         "count": region2.filter(cerrar_evento=False).count(),
            #         "porcentaje": round((((region2.filter(cerrar_evento=False).count()) * 100.00) / region2.count()),2)
            #     },
            #     {
            #         "name": "Abiertos",
            #         "count": region2.filter(cerrar_evento=True).count(),
            #         "porcentaje": round((((region2.filter(cerrar_evento=True).count()) * 100.00) / region2.count()),2)
            #     }
            # ],
            # "region3": [
            #     {
            #         "name": "Finalizados",
            #         "count": region3.filter(cerrar_evento=False).count(),
            #         "porcentaje": round((((region3.filter(cerrar_evento=False).count()) * 100.00) / region3.count()),2)
            #     },
            #     {
            #         "name": "Abiertos",
            #         "count": region3.filter(cerrar_evento=True).count(),
            #         "porcentaje": round((((region3.filter(cerrar_evento=True).count()) * 100.00) / region3.count()),2)
            #     }
            # ],
            # "region4": [
            #     {
            #         "name": "Finalizados",
            #         "count": region4.filter(cerrar_evento=False).count(),
            #         "porcentaje": round((((region4.filter(cerrar_evento=False).count()) * 100.00) / region4.count()),2)
            #     },
            #     {
            #         "name": "Abiertos",
            #         "count": region4.filter(cerrar_evento=True).count(),
            #         "porcentaje": round((((region4.filter(cerrar_evento=True).count()) * 100.00) / region4.count()),2)
            #     }
            # ],
            "porRegion": [
                {
                    "region": "1",
                    "total": region1.count(),
                    "abiertos": region1.filter(cerrar_evento=False).count(),
                    "finalizados": region1.filter(cerrar_evento=True).count()
                },
                {
                    "region": "2",
                    "total": region2.count(),
                    "abiertos": region2.filter(cerrar_evento=False).count(),
                    "finalizados": region2.filter(cerrar_evento=True).count()
                },
                {
                    "region": "3",
                    "total": region3.count(),
                    "abiertos": region3.filter(cerrar_evento=False).count(),
                    "finalizados": region3.filter(cerrar_evento=True).count()
                },
                {
                    "region": "4",
                    "total": region4.count(),
                    "abiertos": region4.filter(cerrar_evento=False).count(),
                    "finalizados": region4.filter(cerrar_evento=True).count()
                },
                {
                    "region": "5",
                    "total": region5.count(),
                    "abiertos": region5.filter(cerrar_evento=False).count(),
                    "finalizados": region5.filter(cerrar_evento=True).count()
                },
                {
                    "region": "6",
                    "total": region6.count(),
                    "abiertos": region6.filter(cerrar_evento=False).count(),
                    "finalizados": region6.filter(cerrar_evento=True).count()
                },
                {
                    "region": "7",
                    "total": region7.count(),
                    "abiertos": region7.filter(cerrar_evento=False).count(),
                    "finalizados": region7.filter(cerrar_evento=True).count()
                }
            ]
        }
        return Response(estadisticas)

    @list_route(methods=['get'])
    def export(self, request):

        inicio = self.request.query_params.get('inicio', None)
        fin = self.request.query_params.get('fin', None)
        region = self.request.query_params.get('region', None)

        eventos = models.EventoDeRobotica.objects.filter(fecha__range=(inicio, fin))

        if region:
            eventos = eventos.filter(escuela__localidad__distrito__region__numero=region)

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="talleres-export.xls"'
        response['Content-Type'] = 'application/vnd.ms-excel'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Talleres')

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Fecha', 'Hora Inicio', 'Hora Fin', 'Título', 'Área', 'Curso', 'Sección', 'Cant. de Alumnos', 'Tallerista', 'Escuela', 'CUE', 'Región', 'Distrito', 'Localidad', 'Docente a Cargo', 'Acta', 'Estado', 'Observaciones', 'Fecha de Creación']
        col_num = 2 # 0 y 1 son obligatorias

        # Escribir los headers
        for col_num in range(len(columns)):
            ws.write(0, col_num, columns[col_num], font_style)

        ws.col(0).width = 256 * 12 # Fecha
        ws.col(1).width = 256 * 12 # Hora Inicio
        ws.col(2).width = 256 * 12 # Hora Fin
        ws.col(3).width = 600 * 12 # Titulo
        ws.col(4).width = 400 * 12 # Área
        ws.col(5).width = 256 * 12 # Curso
        ws.col(6).width = 256 * 12 # Sección
        ws.col(7).width = 256 * 12 # Cantidad de Alumnos
        ws.col(8).width = 600 * 12 # Tallerista
        ws.col(9).width = 600 * 12 # Escuela
        ws.col(10).width = 256 * 12 # CUE
        ws.col(11).width = 200 * 12 # Región
        ws.col(12).width = 400 * 12 # Distrito
        ws.col(13).width = 400 * 12 # Localidad
        ws.col(14).width = 600 * 12 # Docente a Cargo
        ws.col(15).width = 256 * 12 # Acta
        ws.col(16).width = 300 * 12 # Estado
        ws.col(17).width = 600 * 12 # Observaciones
        ws.col(18).width = 256 * 12 # Fecha de Creación

        font_style = xlwt.XFStyle()

        row_num = 0

        for taller in eventos:
            fecha_de_creacion = taller.fecha_de_creacion
            fecha_de_creacion = fecha_de_creacion.strftime("%d-%m-%Y")
            fecha = taller.fecha
            fecha = fecha.strftime("%d-%m-%Y")
            hora_inicio = taller.inicio
            hora_inicio = hora_inicio.strftime("%H:%m")
            hora_fin = taller.fin
            hora_fin = hora_fin.strftime("%H:%m")
            titulo = taller.titulo.nombre
            region = taller.escuela.localidad.distrito.region.numero
            distrito = taller.escuela.localidad.distrito.nombre
            localidad = taller.escuela.localidad.nombre
            cue = taller.escuela.cue
            escuela = taller.escuela.nombre
            tallerista = taller.tallerista.apellido + ", " + taller.tallerista.nombre
            area = taller.area_en_que_se_dicta.nombre
            curso = taller.curso.nombre
            seccion = taller.seccion.nombre
            cantidad_de_alumnos = taller.cantidad_de_alumnos
            docente_a_cargo = taller.docente_a_cargo
            observaciones = taller.minuta
            acta = taller.acta
            if acta:
                acta = "Con Acta"
            else:
                acta = "Sin Acta"

            cerrar_evento = taller.cerrar_evento
            if cerrar_evento == True:
                estado = "Cerrado"
            else:
                estado = "Abierto"

            row_num += 1
            ws.write(row_num, 0, fecha, font_style)
            ws.write(row_num, 1, hora_inicio, font_style)
            ws.write(row_num, 2, hora_fin, font_style)
            ws.write(row_num, 3, titulo, font_style)
            ws.write(row_num, 4, area, font_style)
            ws.write(row_num, 5, curso, font_style)
            ws.write(row_num, 6, seccion, font_style)
            ws.write(row_num, 7, cantidad_de_alumnos, font_style)
            ws.write(row_num, 8, tallerista, font_style)
            ws.write(row_num, 9, escuela, font_style)
            ws.write(row_num, 10, cue, font_style)
            ws.write(row_num, 11, region, font_style)
            ws.write(row_num, 12, distrito, font_style)
            ws.write(row_num, 13, localidad, font_style)
            ws.write(row_num, 14, docente_a_cargo, font_style)
            ws.write(row_num, 15, acta, font_style)
            ws.write(row_num, 16, estado, font_style)
            ws.write(row_num, 17, observaciones, font_style)
            ws.write(row_num, 18, fecha_de_creacion, font_style)

        wb.save(response)
        return(response)
