import 'dart:async';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:mobile/services/api_service.dart';
import 'package:mobile/screens/home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();

  // Controladores y variables de estado para el formulario de registro
  final _dniController = TextEditingController();
  final _codigoController = TextEditingController();
  final _emailController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _isRegisterMode = false;
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _loading = false;
  String? _errorMsg;
  Timer? _errorTimer;

  // Evaluar fuerza de contraseña
  String _passwordStrength = '';
  Color _passwordStrengthColor = Colors.transparent;
  double _passwordStrengthPct = 0.0;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _dniController.dispose();
    _codigoController.dispose();
    _emailController.dispose();
    _confirmPasswordController.dispose();
    _errorTimer?.cancel();
    super.dispose();
  }

  void _evaluarPassword(String value) {
    if (value.isEmpty) {
      setState(() {
        _passwordStrength = '';
        _passwordStrengthColor = Colors.transparent;
        _passwordStrengthPct = 0.0;
      });
      return;
    }

    int score = 0;
    if (value.length >= 6) score++;
    if (value.length >= 10) score++;
    if (RegExp(r'[A-Z]').hasMatch(value)) score++;
    if (RegExp(r'[0-9]').hasMatch(value)) score++;
    if (RegExp(r'[!@#\$&*~%-+=_]').hasMatch(value)) score++;

    setState(() {
      if (score <= 2) {
        _passwordStrength = 'Contraseña Débil ⚠️';
        _passwordStrengthColor = Colors.redAccent;
        _passwordStrengthPct = 0.33;
      } else if (score == 3 || score == 4) {
        _passwordStrength = 'Contraseña Normal 🛡️';
        _passwordStrengthColor = Colors.orangeAccent;
        _passwordStrengthPct = 0.66;
      } else {
        _passwordStrength = 'Contraseña Segura 💪';
        _passwordStrengthColor = const Color(0xFF10B981);
        _passwordStrengthPct = 1.0;
      }
    });
  }

  Future<void> _handleLogin() async {
    final username = _usernameController.text.trim();
    final password = _passwordController.text.trim();

    if (username.isEmpty || password.isEmpty) {
      _showError('Ingresa tu usuario y contraseña.');
      return;
    }

    setState(() {
      _loading = true;
      _errorMsg = null;
    });

    final result = await ApiService.login(username, password);

    if (mounted) {
      setState(() {
        _loading = false;
      });

      if (result['success'] == true) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const HomeScreen()),
        );
      } else {
        _showError(result['message'] ?? 'Credenciales incorrectas.');
      }
    }
  }

  Future<void> _handleRegister() async {
    final dni = _dniController.text.trim();
    final codigo = _codigoController.text.trim().toUpperCase();
    final username = _usernameController.text.trim();
    final email = _emailController.text.trim().toLowerCase();
    final password = _passwordController.text.trim();
    final confirmPassword = _confirmPasswordController.text.trim();

    if (dni.isEmpty || codigo.isEmpty || username.isEmpty || email.isEmpty || password.isEmpty || confirmPassword.isEmpty) {
      _showError('Por favor, completa todos los campos.');
      return;
    }

    if (dni.length != 8 || int.tryParse(dni) == null) {
      _showError('El DNI debe ser un número de exactamente 8 dígitos.');
      return;
    }

    if (!email.contains('@') || email.length < 5) {
      _showError('Ingresa un correo electrónico válido.');
      return;
    }

    if (username.length < 3) {
      _showError('El nombre de usuario debe tener al menos 3 caracteres.');
      return;
    }

    if (password.length < 6) {
      _showError('La contraseña debe tener al menos 6 caracteres.');
      return;
    }

    if (password != confirmPassword) {
      _showError('Las contraseñas ingresadas no coinciden.');
      return;
    }

    setState(() {
      _loading = true;
      _errorMsg = null;
    });

    final result = await ApiService.registrarVinculado(
      dni: dni,
      codigoVinculacion: codigo,
      username: username,
      email: email,
      password: password,
    );

    if (mounted) {
      setState(() {
        _loading = false;
      });

      if (result['success'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('¡Cuenta vinculada y creada con éxito!'),
            backgroundColor: Color(0xFF10B981),
          ),
        );
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const HomeScreen()),
        );
      } else {
        _showError(result['message'] ?? 'Ocurrió un error al vincular la cuenta.');
      }
    }
  }

  void _showError(String message) {
    _errorTimer?.cancel();
    setState(() {
      _errorMsg = message;
    });
    // Ocultar automáticamente en 4 segundos
    _errorTimer = Timer(const Duration(seconds: 4), () {
      if (mounted) {
        setState(() {
          _errorMsg = null;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: isDark ? const Color(0xFF0A1120) : const Color(0xFFF8FAFF),
      body: Stack(
        fit: StackFit.expand,
        children: [
          Positioned(
            top: -80,
            left: -70,
            child: Container(
              width: 240,
              height: 240,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [const Color(0xFF10B981).withValues(alpha: 0.26), Colors.transparent],
                ),
              ),
            ),
          ),
          Positioned(
            top: 140,
            right: -90,
            child: Container(
              width: 220,
              height: 220,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [const Color(0xFF3B82F6).withValues(alpha: 0.16), Colors.transparent],
                ),
              ),
            ),
          ),
          Positioned(
            bottom: -90,
            left: -90,
            child: Container(
              width: 260,
              height: 260,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [const Color(0xFFF59E0B).withValues(alpha: 0.12), Colors.transparent],
                ),
              ),
            ),
          ),
          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24.0),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 400),
                  child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Logo/Icono
                  Center(
                    child: TweenAnimationBuilder<double>(
                      tween: Tween<double>(begin: 0.8, end: 1.0),
                      duration: const Duration(milliseconds: 900),
                      curve: Curves.easeOutBack,
                      builder: (context, value, child) {
                        return Transform.scale(
                          scale: value,
                          child: child,
                        );
                      },
                      child: const NutriSyncLogo(
                        size: 84,
                        color: Color(0xFF10B981),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'NutriSync',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.w900,
                      color: isDark ? Colors.white : const Color(0xFF1F2937),
                      letterSpacing: -0.5,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Tu portal de nutrición y salud',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 14,
                      color: isDark ? Colors.grey[400] : const Color(0xFF6B7280),
                    ),
                  ),
                  const SizedBox(height: 18),
                  AnimatedOpacity(
                    duration: const Duration(milliseconds: 600),
                    opacity: 1.0,
                    child: Wrap(
                      alignment: WrapAlignment.center,
                      spacing: 10,
                      runSpacing: 10,
                      children: const [
                        Chip(
                          backgroundColor: Color(0xFF111827),
                          label: Text('Bienestar', style: TextStyle(color: Colors.white, fontSize: 12)),
                        ),
                        Chip(
                          backgroundColor: Color(0xFF10B981),
                          label: Text('Seguimiento', style: TextStyle(color: Colors.white, fontSize: 12)),
                        ),
                        Chip(
                          backgroundColor: Color(0xFF3B82F6),
                          label: Text('Metas', style: TextStyle(color: Colors.white, fontSize: 12)),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 32),

                  // Mensaje de Error (desaparece solo en 4s)
                  if (_errorMsg != null)
                    AnimatedContainer(
                      duration: const Duration(milliseconds: 300),
                      padding: const EdgeInsets.all(12),
                      margin: const EdgeInsets.only(bottom: 20),
                      decoration: BoxDecoration(
                        color: Colors.redAccent.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.redAccent.withValues(alpha: 0.3)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.error_outline_rounded, color: Colors.redAccent, size: 20),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              _errorMsg!,
                              style: const TextStyle(
                                color: Colors.redAccent,
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    ClipRRect(
                      borderRadius: BorderRadius.circular(28),
                      child: BackdropFilter(
                        filter: ImageFilter.blur(sigmaX: 14, sigmaY: 14),
                        child: Container(
                          padding: const EdgeInsets.all(24),
                          decoration: BoxDecoration(
                            color: isDark ? const Color(0xFF111520).withValues(alpha: 0.88) : Colors.white.withValues(alpha: 0.88),
                            borderRadius: BorderRadius.circular(28),
                            border: Border.all(
                              color: isDark ? Colors.white.withValues(alpha: 0.08) : Colors.grey[200]!.withValues(alpha: 0.65),
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withValues(alpha: isDark ? 0.25 : 0.08),
                                blurRadius: 18,
                                offset: const Offset(0, 12),
                              ),
                            ],
                          ),
                          child: AnimatedCrossFade(
                      duration: const Duration(milliseconds: 300),
                      crossFadeState: _isRegisterMode
                          ? CrossFadeState.showSecond
                          : CrossFadeState.showFirst,
                      firstChild: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // Campo de Usuario
                          const Text(
                            'NOMBRE DE USUARIO',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF90949C),
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _usernameController,
                            style: TextStyle(color: isDark ? Colors.white : Colors.black),
                            decoration: InputDecoration(
                              hintText: 'Ingresa tu usuario',
                              hintStyle: TextStyle(color: Colors.grey[500], fontSize: 14),
                              filled: true,
                              fillColor: isDark ? const Color(0xFF262730) : const Color(0xFFF3F4F6),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide.none,
                              ),
                              prefixIcon: Icon(Icons.person_outline_rounded, color: Colors.grey[500]),
                            ),
                          ),
                          const SizedBox(height: 20),

                          // Campo de Contraseña
                          const Text(
                            'CONTRASEÑA',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF90949C),
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _passwordController,
                            obscureText: _obscurePassword,
                            style: TextStyle(color: isDark ? Colors.white : Colors.black),
                            decoration: InputDecoration(
                              hintText: 'Ingresa tu contraseña',
                              hintStyle: TextStyle(color: Colors.grey[500], fontSize: 14),
                              filled: true,
                              fillColor: isDark ? const Color(0xFF262730) : const Color(0xFFF3F4F6),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide.none,
                              ),
                              prefixIcon: Icon(Icons.lock_outline_rounded, color: Colors.grey[500]),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscurePassword
                                      ? Icons.visibility_off_rounded
                                      : Icons.visibility_rounded,
                                  color: Colors.grey[500],
                                  size: 20,
                                ),
                                onPressed: () {
                                  setState(() {
                                    _obscurePassword = !_obscurePassword;
                                  });
                                },
                              ),
                            ),
                          ),
                          const SizedBox(height: 28),

                          // Botón de Login
                          SizedBox(
                            height: 48,
                            child: ElevatedButton(
                              onPressed: _loading ? null : _handleLogin,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF10B981),
                                foregroundColor: Colors.white,
                                elevation: 0,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              child: _loading
                                  ? const SizedBox(
                                      width: 22,
                                      height: 22,
                                      child: CircularProgressIndicator(
                                        color: Colors.white,
                                        strokeWidth: 2.5,
                                      ),
                                    )
                                  : const Text(
                                      'Iniciar Sesión',
                                      style: TextStyle(
                                        fontSize: 15,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                            ),
                          ),
                          const SizedBox(height: 16),

                          // Botón para alternar a Registro
                          TextButton(
                            onPressed: () {
                              setState(() {
                                _isRegisterMode = true;
                                _errorMsg = null;
                                _passwordStrength = '';
                                _usernameController.clear();
                                _passwordController.clear();
                              });
                            },
                            child: const Text(
                              '¿Tienes un código de vinculación? Activa tu cuenta',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: Color(0xFF10B981),
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                      secondChild: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // Campo de DNI
                          const Text(
                            'DNI DEL PACIENTE',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF90949C),
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _dniController,
                            keyboardType: TextInputType.number,
                            maxLength: 8,
                            style: TextStyle(color: isDark ? Colors.white : Colors.black),
                            decoration: InputDecoration(
                              hintText: 'Ingresa tu DNI',
                              counterText: '',
                              hintStyle: TextStyle(color: Colors.grey[500], fontSize: 14),
                              filled: true,
                              fillColor: isDark ? const Color(0xFF262730) : const Color(0xFFF3F4F6),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide.none,
                              ),
                              prefixIcon: Icon(Icons.badge_outlined, color: Colors.grey[500]),
                            ),
                          ),
                          const SizedBox(height: 16),

                          // Campo de Código
                          const Text(
                            'CÓDIGO DE VINCULACIÓN',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF90949C),
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _codigoController,
                            style: TextStyle(color: isDark ? Colors.white : Colors.black),
                            decoration: InputDecoration(
                              hintText: 'Código de 8 caracteres',
                              hintStyle: TextStyle(color: Colors.grey[500], fontSize: 14),
                              filled: true,
                              fillColor: isDark ? const Color(0xFF262730) : const Color(0xFFF3F4F6),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide.none,
                              ),
                              prefixIcon: Icon(Icons.qr_code_scanner_rounded, color: Colors.grey[500]),
                            ),
                          ),
                          const SizedBox(height: 16),

                          // Campo de Correo
                          const Text(
                            'CORREO ELECTRÓNICO',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF90949C),
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _emailController,
                            keyboardType: TextInputType.emailAddress,
                            style: TextStyle(color: isDark ? Colors.white : Colors.black),
                            decoration: InputDecoration(
                              hintText: 'Correo',
                              hintStyle: TextStyle(color: Colors.grey[500], fontSize: 14),
                              filled: true,
                              fillColor: isDark ? const Color(0xFF262730) : const Color(0xFFF3F4F6),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide.none,
                              ),
                              prefixIcon: Icon(Icons.email_outlined, color: Colors.grey[500]),
                            ),
                          ),
                          const SizedBox(height: 16),

                          // Campo de Usuario
                          const Text(
                            'CREAR USUARIO DE ACCESO',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF90949C),
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _usernameController,
                            style: TextStyle(color: isDark ? Colors.white : Colors.black),
                            decoration: InputDecoration(
                              hintText: 'Nombre del usuario',
                              hintStyle: TextStyle(color: Colors.grey[500], fontSize: 14),
                              filled: true,
                              fillColor: isDark ? const Color(0xFF262730) : const Color(0xFFF3F4F6),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide.none,
                              ),
                              prefixIcon: Icon(Icons.person_outline, color: Colors.grey[500]),
                            ),
                          ),
                          const SizedBox(height: 16),

                          // Campo de Contraseña
                          const Text(
                            'CONTRASEÑA',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF90949C),
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _passwordController,
                            obscureText: _obscurePassword,
                            onChanged: _evaluarPassword,
                            style: TextStyle(color: isDark ? Colors.white : Colors.black),
                            decoration: InputDecoration(
                              hintText: 'Crea tu contraseña',
                              hintStyle: TextStyle(color: Colors.grey[500], fontSize: 14),
                              filled: true,
                              fillColor: isDark ? const Color(0xFF262730) : const Color(0xFFF3F4F6),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide.none,
                              ),
                              prefixIcon: Icon(Icons.lock_outline_rounded, color: Colors.grey[500]),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscurePassword
                                      ? Icons.visibility_off_rounded
                                      : Icons.visibility_rounded,
                                  color: Colors.grey[500],
                                  size: 20,
                                ),
                                onPressed: () {
                                  setState(() {
                                    _obscurePassword = !_obscurePassword;
                                  });
                                },
                              ),
                            ),
                          ),

                          // Barra de Seguridad de Contraseña (en Registro)
                          if (_passwordStrength.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  _passwordStrength,
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: _passwordStrengthColor,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Container(
                              height: 4,
                              decoration: BoxDecoration(
                                color: isDark ? Colors.white12 : Colors.grey[200],
                                borderRadius: BorderRadius.circular(2),
                              ),
                              child: Row(
                                children: [
                                  Expanded(
                                    flex: (_passwordStrengthPct * 100).toInt(),
                                    child: Container(
                                      decoration: BoxDecoration(
                                        color: _passwordStrengthColor,
                                        borderRadius: BorderRadius.circular(2),
                                      ),
                                    ),
                                  ),
                                  Expanded(
                                    flex: ((1 - _passwordStrengthPct) * 100).toInt(),
                                    child: Container(),
                                  ),
                                ],
                              ),
                            ),
                          ],
                          const SizedBox(height: 16),

                          // Campo de Confirmar Contraseña
                          const Text(
                            'CONFIRMAR CONTRASEÑA',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF90949C),
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 8),
                          TextField(
                            controller: _confirmPasswordController,
                            obscureText: _obscureConfirmPassword,
                            style: TextStyle(color: isDark ? Colors.white : Colors.black),
                            decoration: InputDecoration(
                              hintText: 'Confirma tu contraseña',
                              hintStyle: TextStyle(color: Colors.grey[500], fontSize: 14),
                              filled: true,
                              fillColor: isDark ? const Color(0xFF262730) : const Color(0xFFF3F4F6),
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide.none,
                              ),
                              prefixIcon: Icon(Icons.lock_clock_outlined, color: Colors.grey[500]),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscureConfirmPassword
                                      ? Icons.visibility_off_rounded
                                      : Icons.visibility_rounded,
                                  color: Colors.grey[500],
                                  size: 20,
                                ),
                                onPressed: () {
                                  setState(() {
                                    _obscureConfirmPassword = !_obscureConfirmPassword;
                                  });
                                },
                              ),
                            ),
                          ),
                          const SizedBox(height: 28),

                          // Botón de Registro
                          SizedBox(
                            height: 48,
                            child: ElevatedButton(
                              onPressed: _loading ? null : _handleRegister,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF10B981),
                                foregroundColor: Colors.white,
                                elevation: 0,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              child: _loading
                                  ? const SizedBox(
                                      width: 22,
                                      height: 22,
                                      child: CircularProgressIndicator(
                                        color: Colors.white,
                                        strokeWidth: 2.5,
                                      ),
                                    )
                                  : const Text(
                                      'Vincular y Activar Cuenta',
                                      style: TextStyle(
                                        fontSize: 15,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                            ),
                          ),
                          const SizedBox(height: 16),

                          // Botón para volver a Login
                          TextButton(
                            onPressed: () {
                              setState(() {
                                _isRegisterMode = false;
                                _errorMsg = null;
                                _passwordStrength = '';
                                _dniController.clear();
                                _codigoController.clear();
                                _emailController.clear();
                                _usernameController.clear();
                                _passwordController.clear();
                                _confirmPasswordController.clear();
                              });
                            },
                            child: const Text(
                              '¿Ya tienes una cuenta activa? Inicia Sesión',
                              style: TextStyle(
                                color: Color(0xFF10B981),
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ), // Cierra AnimatedCrossFade
                  ), // Cierra Container
                ), // Cierra BackdropFilter
              ), // Cierra ClipRRect
            ], // Cierra children de Column principal
          ), // Cierra Column principal
        ), // Cierra ConstrainedBox
      ), // Cierra SingleChildScrollView
    ), // Cierra Center
  ), // Cierra SafeArea
], // Cierra children de Stack
      ), // Cierra Stack
    ); // Cierra Scaffold
  }
}

// ─── Logo Personalizado Vectorial de NutriSync (Manzana) ──────────────────────
class NutriSyncLogo extends StatelessWidget {
  final double size;
  final Color color;

  const NutriSyncLogo({
    super.key,
    this.size = 80,
    this.color = const Color(0xFF10B981),
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: AppleLogoPainter(color: color),
      ),
    );
  }
}

class AppleLogoPainter extends CustomPainter {
  final Color color;

  AppleLogoPainter({this.color = const Color(0xFF10B981)});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.5
      ..strokeCap = StrokeCap.round
      ..isAntiAlias = true;

    final path = Path();
    final w = size.width;
    final h = size.height;

    // Cuerpo de la manzana
    // Empezamos en el centro superior (depresión superior)
    path.moveTo(w * 0.5, h * 0.32);
    
    // Curva hacia la izquierda y abajo
    path.cubicTo(
      w * 0.22, h * 0.16, // Control 1
      w * 0.05, h * 0.42, // Control 2
      w * 0.12, h * 0.68  // Punto final izquierdo-bajo
    );
    
    // Curva hacia la base de la manzana (depresión inferior)
    path.cubicTo(
      w * 0.18, h * 0.88, // Control 1
      w * 0.40, h * 0.94, // Control 2
      w * 0.50, h * 0.86  // Punto central inferior
    );
    
    // Curva hacia la derecha-bajo y arriba
    path.cubicTo(
      w * 0.60, h * 0.94, // Control 1
      w * 0.82, h * 0.88, // Control 2
      w * 0.88, h * 0.68  // Punto final derecho-bajo
    );
    
    // Curva hacia el centro superior
    path.cubicTo(
      w * 0.95, h * 0.42, // Control 1
      w * 0.78, h * 0.16, // Control 2
      w * 0.50, h * 0.32  // Volver al inicio superior
    );
    
    // Dibujar el cuerpo
    canvas.drawPath(path, paint);

    // Tallo (Stem)
    final stemPath = Path();
    stemPath.moveTo(w * 0.5, h * 0.30);
    stemPath.quadraticBezierTo(
      w * 0.46, h * 0.16, // Punto de control
      w * 0.52, h * 0.10  // Final del tallo
    );
    canvas.drawPath(stemPath, paint);

    // Hoja (Leaf)
    final leafPath = Path();
    leafPath.moveTo(w * 0.52, h * 0.16);
    // Forma de la hoja
    leafPath.quadraticBezierTo(w * 0.70, h * 0.08, w * 0.76, h * 0.04);
    leafPath.quadraticBezierTo(w * 0.66, h * 0.22, w * 0.52, h * 0.16);
    
    final leafPaint = Paint()
      ..color = color
      ..style = PaintingStyle.fill
      ..isAntiAlias = true;
      
    canvas.drawPath(leafPath, leafPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
