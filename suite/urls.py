from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token


from easy_pdf.views import PDFTemplateView

import escuelas.views.aplicacion
import escuelas.views.area
import escuelas.views.area_de_robotica
import escuelas.views.cargo
import escuelas.views.cargo_escolar
import escuelas.views.categoria_de_evento
import escuelas.views.comentario_de_tarea
import escuelas.views.comentario_de_validacion
import escuelas.views.contacto
import escuelas.views.contrato
import escuelas.views.curso_de_robotica
import escuelas.views.distribucion_de_paquete
import escuelas.views.distrito
import escuelas.views.eje_de_robotica
import escuelas.views.escuela
import escuelas.views.estado_de_paquete
import escuelas.views.estado_de_tarea
import escuelas.views.estado_de_validacion
import escuelas.views.evento
import escuelas.views.evento_de_robotica
import escuelas.views.experiencia
import escuelas.views.group
import escuelas.views.home
import escuelas.views.localidad
import escuelas.views.mi_perfil
import escuelas.views.modalidad
import escuelas.views.motivo_de_conformacion
import escuelas.views.motivo_de_tarea
import escuelas.views.nivel
import escuelas.views.paquete
import escuelas.views.perfil
import escuelas.views.permission
import escuelas.views.piso
import escuelas.views.prioridad_de_tarea
import escuelas.views.programa
import escuelas.views.region
import escuelas.views.rol_en_robotica
import escuelas.views.seccion_de_robotica
import escuelas.views.taller_de_robotica
import escuelas.views.tarea
import escuelas.views.tipo_de_financiamiento
import escuelas.views.tipo_de_gestion
import escuelas.views.user
import escuelas.views.validacion
from escuelas import views
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)

router.register('aplicaciones', escuelas.views.aplicacion.AplicacionViewSet)
router.register('users', escuelas.views.user.UserViewSet)
router.register('escuelas', escuelas.views.escuela.EscuelaViewSet)
router.register('contactos', escuelas.views.contacto.ContactoViewSet)
router.register('eventos', escuelas.views.evento.EventoViewSet)
router.register('eventos-de-robotica', escuelas.views.evento_de_robotica.EventoDeRoboticaViewSet)
router.register('regiones', escuelas.views.region.RegionViewSet)
router.register('perfiles', escuelas.views.perfil.PerfilViewSet)
router.register('distritos', escuelas.views.distrito.DistritoViewSet)
router.register('localidades', escuelas.views.localidad.LocalidadViewSet)
router.register('programas', escuelas.views.programa.ProgramaViewSet)
router.register('tipos-de-financiamiento', escuelas.views.tipo_de_financiamiento.TipoDeFinanciamientoViewSet)
router.register('tipos-de-gestion', escuelas.views.tipo_de_gestion.TipoDeGestionViewSet)
router.register('areas', escuelas.views.area.AreaViewSet)
router.register('areas-de-robotica', escuelas.views.area_de_robotica.AreaDeRoboticaViewSet)
router.register('cursos-de-robotica', escuelas.views.curso_de_robotica.CursoDeRoboticaViewSet)
router.register('ejes-de-robotica', escuelas.views.eje_de_robotica.EjeDeRoboticaViewSet)
router.register('secciones-de-robotica', escuelas.views.seccion_de_robotica.SeccionDeRoboticaViewSet)
router.register('talleres-de-robotica', escuelas.views.taller_de_robotica.TallerDeRoboticaViewSet)
router.register('niveles', escuelas.views.nivel.NivelViewSet)
router.register('modalidades', escuelas.views.modalidad.ModalidadViewSet)
router.register('experiencias', escuelas.views.experiencia.ExperienciaViewSet)
router.register('cargos', escuelas.views.cargo.CargoViewSet)
router.register('roles-en-robotica', escuelas.views.rol_en_robotica.RolEnRoboticaViewSet)
router.register('contratos', escuelas.views.contrato.ContratoViewSet)
router.register('pisos', escuelas.views.piso.PisoViewSet)
router.register('cargos-escolares', escuelas.views.cargo_escolar.CargoEscolarViewSet)
router.register('comentario-de-tareas', escuelas.views.comentario_de_tarea.ComentarioDeTareaViewSet)
router.register('motivo-de-tareas', escuelas.views.motivo_de_tarea.MotivoDeTareaViewSet)
router.register('motivos-de-conformacion', escuelas.views.motivo_de_conformacion.MotivoDeConformacionViewSet)
router.register('estado-de-tareas', escuelas.views.estado_de_tarea.EstadoDeTareaViewSet)
router.register('prioridad-de-tareas', escuelas.views.prioridad_de_tarea.PrioridadDeTareaViewSet)
router.register('tareas', escuelas.views.tarea.TareaViewSet)
router.register('categorias-de-eventos', escuelas.views.categoria_de_evento.CategoriaDeEventoViewSet)
router.register('comentarios-de-validacion', escuelas.views.comentario_de_validacion.ComentarioDeValidacionViewSet)
router.register('validaciones', escuelas.views.validacion.ValidacionViewSet)
router.register('estados-de-validacion', escuelas.views.estado_de_validacion.EstadoDeValidacionViewSet)
router.register('estados-de-paquete', escuelas.views.estado_de_paquete.EstadoDePaqueteViewSet)
router.register('paquetes', escuelas.views.paquete.PaqueteViewSet)
router.register('permissions', escuelas.views.permission.PermissionViewSet)
router.register('groups', escuelas.views.group.GroupViewSet)
router.register('informes', views.informes.InformesViewSet, 'Informes')
router.register('trabajos', views.trabajos.TrabajosViewSet, 'Trabajos')
router.register('distribucion-de-paquetes', escuelas.views.distribucion_de_paquete.DistribucionDePaquetesViewSet, 'DistribucionDePaquetes')
router.register('mi-perfil', escuelas.views.mi_perfil.MiPerfilViewSet, 'Perfil')

urlpatterns = [
    url(r'^$', escuelas.views.home, name='home'),
    url(r'^api/', include(router.urls)),
    url(r'^api/auth', obtain_auth_token),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^django-rq/', include('django_rq.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
