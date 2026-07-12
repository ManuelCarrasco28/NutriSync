import 'package:flutter/material.dart';
import 'package:mobile/services/api_service.dart';

class PlanTab extends StatefulWidget {
  const PlanTab({super.key});

  @override
  State<PlanTab> createState() => _PlanTabState();
}

class _PlanTabState extends State<PlanTab> {
  bool _loading = false;
  List<dynamic> _comidas = [];
  String? _planNombre;
  String? _errorMsg;

  @override
  void initState() {
    super.initState();
    _cargarPlan();
  }

  Future<void> _cargarPlan() async {
    setState(() {
      _loading = true;
      _errorMsg = null;
    });

    try {
      final plan = await ApiService.getPlanActivo();
      if (mounted) {
        setState(() {
          _comidas = plan['comidas'] ?? [];
          _planNombre = plan['nombre'] ?? 'Plan Alimentario';
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMsg = 'No se pudo cargar tu plan alimentario activo. Revisa tu conexión.';
          _loading = false;
        });
      }
    }
  }

  String _formatearHora(String? horaStr) {
    if (horaStr == null || horaStr.isEmpty) return '';
    try {
      final partes = horaStr.split(':');
      if (partes.length < 2) return horaStr;
      final hora = int.parse(partes[0]);
      final minutos = int.parse(partes[1]);
      
      final periodo = hora >= 12 ? 'PM' : 'AM';
      var hora12 = hora % 12;
      if (hora12 == 0) hora12 = 12;
      
      final minsStr = minutos.toString().padLeft(2, '0');
      final horasStr = hora12.toString().padLeft(2, '0');
      
      return '$horasStr:$minsStr $periodo';
    } catch (e) {
      return horaStr;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textThemeColor = isDark ? Colors.white : const Color(0xFF1F2937);
    final cardColor = isDark ? const Color(0xFF1C1D24) : Colors.white;

    if (_loading && _comidas.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(color: Color(0xFF10B981)),
      );
    }

    return RefreshIndicator(
      onRefresh: _cargarPlan,
      color: const Color(0xFF10B981),
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16.0),
        children: [
          Text(
            '🍎 Menú Sugerido',
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF10B981),
              letterSpacing: -0.5,
            ),
          ),
          if (_planNombre != null) ...[
            const SizedBox(height: 4),
            Text(
              _planNombre!,
              style: TextStyle(
                fontSize: 13,
                color: isDark ? Colors.grey[400] : const Color(0xFF6B7280),
              ),
            ),
          ],
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF111827) : const Color(0xFFF3F4F6),
              borderRadius: BorderRadius.circular(18),
            ),
            child: const Text(
              'Plan recomendado con tus comidas del día y metas nutricionales.',
              style: TextStyle(fontSize: 13, height: 1.5),
            ),
          ),
          const SizedBox(height: 20),

          if (_errorMsg != null)
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF111827) : Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: isDark ? Colors.white.withValues(alpha: 0.04) : Colors.grey[200]!,
                ),
              ),
              child: Column(
                children: [
                  const Icon(Icons.wifi_off_rounded, color: Colors.redAccent, size: 44),
                  const SizedBox(height: 12),
                  Text(
                    _errorMsg!,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 13,
                      height: 1.4,
                      color: isDark ? Colors.grey[300] : const Color(0xFF4B5563),
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: _cargarPlan,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF10B981),
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    icon: const Icon(Icons.refresh_rounded, size: 18),
                    label: const Text('Reintentar', style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            )
          else if (_comidas.isEmpty)
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: cardColor,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: isDark ? Colors.white.withValues(alpha: 0.04) : Colors.grey[200]!,
                ),
              ),
              child: Text(
                'Tu plan alimenticio no registra comidas específicas asignadas aún para hoy.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: isDark ? Colors.grey[400] : const Color(0xFF6B7280),
                  fontStyle: FontStyle.italic,
                ),
              ),
            )
          else
            ..._comidas.map((comida) {
              final String tipo = (comida['tipo'] ?? comida['tipo_comida'] ?? '').toString().toUpperCase();
              final int cals = comida['calorias_estimadas'] ?? 350;
              
              String desc = '';
              if (comida['alimentos'] != null) {
                desc = '${comida['alimentos']}';
                final cant = comida['cantidad'] ?? '';
                final unid = comida['unidad'] ?? '';
                if (cant.toString().isNotEmpty || unid.toString().isNotEmpty) {
                  desc += '\n⚖️ Cantidad: $cant $unid';
                }
                final obs = comida['observaciones'] ?? '';
                if (obs.toString().isNotEmpty) {
                  desc += '\n💡 Nota: $obs';
                }
              } else {
                desc = comida['descripcion'] ?? '';
              }

              final hora = comida['hora'] as String?;

              return Container(
                margin: const EdgeInsets.only(bottom: 14),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: isDark
                        ? const [Color(0xFF111827), Color(0xFF1F2937)]
                        : const [Color(0xFFFFFFFF), Color(0xFFF7FBFF)],
                  ),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: isDark ? Colors.white.withValues(alpha: 0.04) : Colors.grey[200]!,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: isDark ? 0.14 : 0.05),
                      blurRadius: 14,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Text(
                              tipo,
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w900,
                                color: Color(0xFF10B981),
                              ),
                            ),
                            if (hora != null && hora.isNotEmpty) ...[
                              const SizedBox(width: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF10B981).withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  '⏰ ${_formatearHora(hora)}',
                                  style: const TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF10B981),
                                  ),
                                ),
                              ),
                            ],
                          ],
                        ),
                        Text(
                          '$cals kcal',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            color: textThemeColor,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(
                      desc,
                      style: TextStyle(
                        fontSize: 14,
                        height: 1.5,
                        color: isDark ? Colors.grey[300] : const Color(0xFF374151),
                      ),
                    ),
                  ],
                ),
              );
            }),
        ],
      ),
    );
  }
}
