from django.contrib.auth.models import User
from rest_framework import serializers
import models
from rest_framework_json_api.relations import ResourceRelatedField
from django.contrib.auth.models import Permission, Group
import json

class CustomSerializer(serializers.HyperlinkedModelSerializer):

    def get_field_names(self, declared_fields, info):
        expanded_fields = super(CustomSerializer, self).get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields

        return expanded_fields

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff', 'password')

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class ContactoSerializer(CustomSerializer):

    escuela = ResourceRelatedField(queryset=models.Escuela.objects)
    cargo = ResourceRelatedField(queryset=models.CargoEscolar.objects)

    class Meta:
        model = models.Contacto
        fields = ('nombre', 'telefono_particular', 'telefono_celular', 'horario', 'email', 'escuela', 'cargo')

class EventoSerializer(CustomSerializer):

    responsable = ResourceRelatedField(queryset=models.Perfil.objects)
    escuela = ResourceRelatedField(queryset=models.Escuela.objects)
    categoria = ResourceRelatedField(queryset=models.CategoriaDeEvento.objects)
    acompaniantes = ResourceRelatedField(queryset=models.Perfil.objects, many=True)

    class Meta:
        model = models.Evento
        fields = ('id', 'titulo', 'region', 'fecha', 'fecha_fin', 'inicio', 'fin', 'objetivo', 'responsable', 'escuela', 'acompaniantes', 'cantidad_de_participantes', 'requiere_traslado', 'categoria', 'resumenParaCalendario', 'minuta', 'acta_legacy', 'legacy_id', 'acta','fecha_de_creacion', 'fecha_de_ultima_modificacion')
        read_only_fields = ['acta', 'region']

class EventoDeRoboticaSerializer(CustomSerializer):

    tallerista = ResourceRelatedField(queryset=models.Perfil.objects)
    escuela = ResourceRelatedField(queryset=models.Escuela.objects)
    titulo = ResourceRelatedField(queryset=models.TallerDeRobotica.objects)
    curso = ResourceRelatedField(queryset=models.CursoDeRobotica.objects)
    seccion = ResourceRelatedField(queryset=models.SeccionDeRobotica.objects)
    area_en_que_se_dicta = ResourceRelatedField(queryset=models.AreaDeRobotica.objects)
    fecha_formateada = serializers.SerializerMethodField()
    fecha_de_creacion_formateada = serializers.SerializerMethodField()

    class Meta:
        model = models.EventoDeRobotica
        fields = ('id', 'titulo', 'curso', 'seccion', 'docente_a_cargo', 'area_en_que_se_dicta', 'fecha', 'inicio', 'fin', 'tallerista', 'escuela', 'cantidad_de_alumnos', 'minuta', 'acta', 'cerrar_evento', 'fecha_formateada', 'fecha_de_ultima_modificacion', 'fecha_de_creacion', 'fecha_de_creacion_formateada', 'resumenParaCalendario', 'se_dio_el_taller', 'motivo')
        read_only_fields = ['acta']

    def get_fecha_formateada(self, objeto):
        return "{} de {} hs a {} hs".format(
            objeto.fecha.strftime('%d/%m/%Y'),
            objeto.inicio.strftime("%H:%M"),
            objeto.fin.strftime("%H:%M"))

    def get_fecha_de_creacion_formateada(self, objeto):
        return "{}".format(
            objeto.fecha_de_creacion.strftime('%d/%m/%Y'))

class RegionSerializer(CustomSerializer):

    class Meta:
        model = models.Region
        fields = "__all__"


class CargoSerializer(CustomSerializer):

    class Meta:
        model = models.Cargo
        fields = '__all__'

class RolEnRoboticaSerializer(CustomSerializer):

    class Meta:
        model = models.RolEnRobotica
        fields = '__all__'

class PerfilSerializer(CustomSerializer):

    cargo = ResourceRelatedField(queryset=models.Cargo.objects)
    rol_en_robotica = ResourceRelatedField(queryset=models.RolEnRobotica.objects)
    region = ResourceRelatedField(queryset=models.Region.objects)
    contrato = ResourceRelatedField(queryset=models.Contrato.objects)
    localidad = ResourceRelatedField(queryset=models.Localidad.objects)
    group = ResourceRelatedField(queryset=Group.objects)
    aplicaciones = ResourceRelatedField(queryset=models.Aplicacion.objects, many=True)

    class Meta:
        model = models.Perfil
        fields = ('user', 'group', 'image', 'nombre', 'apellido', 'fechadenacimiento', 'titulo', 'experiencia', 'dni', 'cuit', 'cbu', 'email', 'estado', 'direccion_calle', 'direccion_altura', 'direccion_piso', 'direccion_depto', 'direccion_torre', 'codigo_postal', 'localidad', 'telefono_celular', 'telefono_alternativo', 'region', 'cargo', 'contrato', 'expediente', 'fecha_de_ingreso', 'fecha_de_renuncia', 'email_laboral', 'aplicaciones', 'rol_en_robotica')
        read_only_fields = ('image',)

class DistritoSerializer(CustomSerializer):

    region = RegionSerializer()

    class Meta:
        model = models.Distrito
        fields = "__all__"

class LocalidadSerializer(CustomSerializer):

    distrito = DistritoSerializer()

    class Meta:
        model = models.Localidad
        fields = "__all__"

class ProgramaSerializer(CustomSerializer):

    escuelas = ResourceRelatedField(queryset=models.Perfil.objects, many=True)

    class Meta:
        model = models.Programa
        fields = ('id', 'nombre', 'escuelas')
        # extra_fields = ['cantidadDeEscuelas']

class TipoDeFinanciamientoSerializer(CustomSerializer):

    class Meta:
        model = models.TipoDeFinanciamiento
        fields = "__all__"

class TipoDeGestionSerializer(CustomSerializer):

    class Meta:
        model = models.TipoDeGestion
        fields = "__all__"

class AreaSerializer(CustomSerializer):

    class Meta:
        model = models.Area
        fields = "__all__"

class NivelSerializer(CustomSerializer):

    class Meta:
        model = models.Nivel
        fields = "__all__"

class ModalidadSerializer(CustomSerializer):

    class Meta:
        model = models.Modalidad
        fields = "__all__"

class PisoSerializer(CustomSerializer):
    escuela = ResourceRelatedField(queryset=models.Escuela.objects, allow_null=True)

    class Meta:
        model = models.Piso
        fields = '__all__'
        read_only_fields = ['llave']

class DistribucionDePaqueteSerializer(CustomSerializer):

    class Meta:
        model = models.DistribucionDePaquete
        fields = ('archivo', 'fecha')
        read_only_fields = ['archivo']

class MotivoDeConformacionSerializer(CustomSerializer):

    class Meta:
        model = models.MotivoDeConformacion
        fields = "__all__"

class SubEscuelaSerializer(CustomSerializer):

    class Meta:
        model = models.Escuela
        fields = ('cue', 'nombre',)

class EscuelaSerializer(CustomSerializer):

    localidad = ResourceRelatedField(queryset=models.Localidad.objects)
    tipo_de_financiamiento = ResourceRelatedField(queryset=models.TipoDeFinanciamiento.objects, many=True)
    nivel = ResourceRelatedField(queryset=models.Nivel.objects)
    modalidad = ResourceRelatedField(queryset=models.Modalidad.objects, required=False, allow_null=True)
    tipo_de_gestion = ResourceRelatedField(queryset=models.TipoDeGestion.objects)
    area = ResourceRelatedField(queryset=models.Area.objects)
    programas = ResourceRelatedField(queryset=models.Programa.objects, many=True)
    piso = ResourceRelatedField(queryset=models.Piso.objects)
    contactos = ContactoSerializer(many=True, read_only=True)
    subescuelas = SubEscuelaSerializer(many=True, read_only=True)
    padre = ResourceRelatedField(read_only=True)
    motivo_de_conformacion = ResourceRelatedField(read_only=True)
    validaciones = ResourceRelatedField(read_only=True, many=True)
    perfil_de_ultima_modificacion = ResourceRelatedField(queryset=models.Perfil.objects)

    class Meta:
        model = models.Escuela
        fields = ('cue', 'nombre', 'direccion', 'telefono', 'email', 'latitud', 'longitud', 'localidad', 'tipo_de_financiamiento', 'nivel', 'modalidad', 'tipo_de_gestion', 'area', 'programas', 'piso', 'contactos', 'padre', 'fecha_conformacion', 'motivo_de_conformacion', 'estado', 'conformada', 'padre', 'subescuelas', 'validaciones', 'numero_de_region', 'observaciones', 'fecha_de_ultima_modificacion', 'perfil_de_ultima_modificacion')


class ExperienciaSerializer(CustomSerializer):

    class Meta:
        model = models.Experiencia
        fields = '__all__'


class ContratoSerializer(CustomSerializer):

    class Meta:
        model = models.Contrato
        fields = '__all__'

class CargoEscolarSerializer(CustomSerializer):

    class Meta:
        model = models.CargoEscolar
        fields = '__all__'

class ComentarioDeTareaSerializer(CustomSerializer):

    class Meta:
        model = models.ComentarioDeTarea
        fields = '__all__'

class MotivoDeTareaSerializer(CustomSerializer):

    class Meta:
        model = models.MotivoDeTarea
        fields = '__all__'

class EstadoDeTareaSerializer(CustomSerializer):

    class Meta:
        model = models.EstadoDeTarea
        fields = '__all__'

class PrioridadDeTareaSerializer(CustomSerializer):

    class Meta:
        model = models.PrioridadDeTarea
        fields = '__all__'

class TareaSerializer(CustomSerializer):
    autor = ResourceRelatedField(queryset=models.Perfil.objects)
    responsable = ResourceRelatedField(queryset=models.Perfil.objects)
    motivo_de_tarea = ResourceRelatedField(queryset=models.MotivoDeTarea.objects)
    estado_de_tarea = ResourceRelatedField(queryset=models.EstadoDeTarea.objects)
    prioridad_de_tarea = ResourceRelatedField(queryset=models.PrioridadDeTarea.objects)
    escuela = ResourceRelatedField(queryset=models.Escuela.objects)
    # comentarios_tarea = ComentarioDeTareaSerializer(many=True, read_only=True)
    # comentarios_de_tarea = ResourceRelatedField(queryset=models.ComentarioDeTarea.objects, many=True)

    class Meta:
        model = models.Tarea
        fields = ('titulo', 'fecha_de_alta', 'autor', 'responsable', 'descripcion', 'motivo_de_tarea', 'estado_de_tarea', 'prioridad_de_tarea', 'escuela')

class CategoriaDeEventoSerializer(CustomSerializer):

    class Meta:
        model = models.CategoriaDeEvento
        fields = '__all__'

class TallerDeRoboticaSerializer(CustomSerializer):

    ejes = ResourceRelatedField(queryset=models.EjeDeRobotica.objects, many=True)

    class Meta:
        model = models.TallerDeRobotica
        fields = ('nombre', 'area', 'ejes')

class AreaDeRoboticaSerializer(CustomSerializer):

    class Meta:
        model = models.AreaDeRobotica
        fields = '__all__'

class CursoDeRoboticaSerializer(CustomSerializer):

    class Meta:
        model = models.CursoDeRobotica
        fields = '__all__'

class SeccionDeRoboticaSerializer(CustomSerializer):

    class Meta:
        model = models.SeccionDeRobotica
        fields = '__all__'

class EjeDeRoboticaSerializer(CustomSerializer):

    class Meta:
        model = models.EjeDeRobotica
        fields = '__all__'

class EstadoDeValidacionSerializer(CustomSerializer):

    class Meta:
        model = models.EstadoDeValidacion
        fields = '__all__'


class ComentarioDeValidacionSerializer(CustomSerializer):

    autor = ResourceRelatedField(queryset=models.Perfil.objects)

    class Meta:
        model = models.ComentarioDeValidacion
        fields = '__all__'

class ValidacionSerializer(CustomSerializer):
    autor = ResourceRelatedField(queryset=models.Perfil.objects)
    escuela = ResourceRelatedField(queryset=models.Escuela.objects)
    estado = ResourceRelatedField(queryset=models.EstadoDeValidacion.objects)
    # comentariosDeValidacion = ResourceRelatedField(queryset=models.ComentarioDeValidacion.objects, many=True)

    class Meta:
        model = models.Validacion
        fields = ('autor', 'fecha_de_alta', 'fecha_de_modificacion', 'escuela', 'estado', 'cantidad_pedidas', 'cantidad_validadas', 'observaciones')


class EstadoDePaqueteSerializer(CustomSerializer):

    class Meta:
        model = models.EstadoDePaquete
        fields = '__all__'

class PaqueteSerializer(CustomSerializer):

    escuela = ResourceRelatedField(queryset=models.Escuela.objects)
    estado = ResourceRelatedField(queryset=models.EstadoDePaquete.objects)
    perfil_que_solicito_el_paquete = ResourceRelatedField(queryset=models.Perfil.objects)

    class Meta:
        model = models.Paquete
        fields = (
            'escuela',
            'fecha_pedido',
            'ne',
            'id_hardware',
            'marca_de_arranque',
            'comentario',
            'carpeta_paquete',
            'fecha_envio',
            'zip_paquete',
            'estado',
            'fecha_devolucion',
            'id_devolucion',
            'leido',
            'tpmdata',
            'ma_hexa',
            'zip_devolucion',
            'perfil_que_solicito_el_paquete'
        )
        read_only_fields = ['zip_devolucion']

class PermissionSerializer(CustomSerializer):
    content_type = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = Permission
        fields = ('name', 'codename', 'content_type')

class GroupSerializer(CustomSerializer):
    perfiles = ResourceRelatedField(read_only=True, many=True)
    permissions = ResourceRelatedField(read_only=True, many=True)

    class Meta:
        model = Group
        fields = ('url', 'name', 'perfiles', 'permissions')

class AplicacionSerializer(CustomSerializer):

    class Meta:
        model = models.Aplicacion
        fields = '__all__'
