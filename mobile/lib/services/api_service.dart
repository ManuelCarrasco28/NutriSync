import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // URL base por defecto para emulador Android.
  // Si ejecutas en un dispositivo físico, usa la IP local de tu PC.
  // Ejemplo de uso:
  // flutter run -d <device> --dart-define=API_BASE_URL=http://192.168.101.18:8000/api/paciente
  static final String baseUrl = const String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: '',
  ).isNotEmpty
      ? const String.fromEnvironment('API_BASE_URL')
      : _defaultLocalUrl();

  static String _defaultLocalUrl() {
    if (Platform.isAndroid) {
      return 'http://192.168.101.18:8000/api/paciente';
    }
    return 'http://10.0.2.2:8000/api/paciente';
  }

  static String? _token;
  static String? _nombrePaciente;
  static String? _email;

  // Inicializar SharedPreferences y cargar el token si existe
  static Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('token');
    _nombrePaciente = prefs.getString('nombre_paciente');
    _email = prefs.getString('email');
  }

  static bool get isAuthenticated => _token != null;
  static String? get token => _token;
  static String? get nombrePaciente => _nombrePaciente;
  static String? get email => _email;

  // Guardar datos de sesión
  static Future<void> guardarSesion(String tokenValue, String nombreValue, String emailValue) async {
    _token = tokenValue;
    _nombrePaciente = nombreValue;
    _email = emailValue;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', tokenValue);
    await prefs.setString('nombre_paciente', nombreValue);
    await prefs.setString('email', emailValue);
  }

  // Borrar datos de sesión (Logout)
  static Future<void> cerrarSesion() async {
    _token = null;
    _nombrePaciente = null;
    _email = null;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    await prefs.remove('nombre_paciente');
    await prefs.remove('email');
  }

  // Interceptor para agregar Token Bearer a los headers
  static Map<String, String> _getHeaders() {
    final Map<String, String> headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (_token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    return headers;
  }

  // Petición POST de Login
  static Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      final decoded = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 200) {
        final tokenVal = decoded['token'] as String;
        final nombreVal = decoded['nombre_paciente'] as String;
        final emailVal = decoded['email'] as String;
        await guardarSesion(tokenVal, nombreVal, emailVal);
        return {'success': true};
      } else {
        return {'success': false, 'message': decoded['detail'] ?? 'Credenciales incorrectas.'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Ocurrió un error en la solicitud.'};
    }
  }

  // Petición POST de Registro Vinculado
  static Future<Map<String, dynamic>> registrarVinculado({
    required String dni,
    required String codigoVinculacion,
    required String username,
    required String email,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register-vinculado'),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode({
          'dni': dni,
          'codigo_vinculacion': codigoVinculacion,
          'username': username,
          'email': email,
          'password': password,
        }),
      );

      final decoded = jsonDecode(utf8.decode(response.bodyBytes));
      if (response.statusCode == 200) {
        final tokenVal = decoded['token'] as String;
        final nombreVal = decoded['nombre_paciente'] as String;
        final emailVal = decoded['email'] as String;
        await guardarSesion(tokenVal, nombreVal, emailVal);
        return {'success': true};
      } else {
        return {'success': false, 'message': decoded['detail'] ?? 'El DNI o código ingresado no son válidos.'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Ocurrió un error en la solicitud.'};
    }
  }

  // Obtener Perfil del Paciente
  static Future<Map<String, dynamic>> getPerfil() async {
    final response = await http.get(
      Uri.parse('$baseUrl/perfil'),
      headers: _getHeaders(),
    );
    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } else {
      throw Exception('Error al cargar perfil.');
    }
  }

  // Actualizar Perfil (Teléfono y Avatar)
  static Future<Map<String, dynamic>> updatePerfil({
    required String nombre,
    required String apellido,
    required String telefono,
    required String email,
    String? avatarColor,
    String? fotoUrl,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/perfil/update'),
      headers: _getHeaders(),
      body: jsonEncode({
        'nombre': nombre,
        'apellido': apellido,
        'telefono': telefono,
        'email': email,
        'avatar_color': avatarColor,
        'foto_url': fotoUrl,
      }),
    );
    
    final decoded = jsonDecode(utf8.decode(response.bodyBytes));
    if (response.statusCode == 200) {
      if (decoded['nombre_paciente'] != null) {
        _nombrePaciente = decoded['nombre_paciente'];
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('nombre_paciente', _nombrePaciente!);
      }
      return decoded as Map<String, dynamic>;
    } else {
      throw Exception(decoded['detail'] ?? 'Error al actualizar perfil.');
    }
  }

  // Obtener Plan Alimentario Activo
  static Future<Map<String, dynamic>> getPlanActivo() async {
    final response = await http.get(
      Uri.parse('$baseUrl/plan-activo'),
      headers: _getHeaders(),
    );
    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } else {
      throw Exception('Error al cargar plan alimenticio.');
    }
  }

  // Obtener Historial de Medidas
  static Future<List<dynamic>> getMedidas() async {
    final response = await http.get(
      Uri.parse('$baseUrl/medidas'),
      headers: _getHeaders(),
    );
    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as List<dynamic>;
    } else {
      throw Exception('Error al cargar historial de medidas.');
    }
  }

  // Obtener Citas Programadas
  static Future<List<dynamic>> getCitas() async {
    final response = await http.get(
      Uri.parse('$baseUrl/citas'),
      headers: _getHeaders(),
    );
    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as List<dynamic>;
    } else {
      throw Exception('Error al cargar citas.');
    }
  }

  // Obtener Notas Clínicas
  static Future<List<dynamic>> getNotas() async {
    final response = await http.get(
      Uri.parse('$baseUrl/notas'),
      headers: _getHeaders(),
    );
    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as List<dynamic>;
    } else {
      throw Exception('Error al cargar notas clínicas.');
    }
  }

  // Obtener Recomendaciones
  static Future<List<dynamic>> getRecomendaciones() async {
    final response = await http.get(
      Uri.parse('$baseUrl/recomendaciones'),
      headers: _getHeaders(),
    );
    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as List<dynamic>;
    } else {
      throw Exception('Error al cargar recomendaciones.');
    }
  }

  // Obtener Archivos del Paciente
  static Future<List<dynamic>> getArchivos() async {
    final response = await http.get(
      Uri.parse('$baseUrl/archivos'),
      headers: _getHeaders(),
    );
    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as List<dynamic>;
    } else {
      throw Exception('Error al cargar archivos.');
    }
  }
}
