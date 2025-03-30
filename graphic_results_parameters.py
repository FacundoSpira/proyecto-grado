import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Leer los datos del CSV
data = pd.read_csv('results_parameters_vf.csv')

# Normalizar las métricas para una mejor comparación visual
metrics = ['m_curricula', 'm_coincidencia', 'm_estudiantes', 'm_previas']
data_norm = data.copy()

for metric in metrics:
    if metric == 'm_estudiantes':
        # Para estudiantes afectados (menor es mejor), invertimos la escala
        max_val = data[metric].max()
        # Normalizar como "estudiantes no afectados"
        data_norm[f'{metric}_norm'] = 1 - (data[metric] / max_val)
    else:
        # Para las otras métricas (mayor es mejor), normalizamos directamente
        min_val = data[metric].min()
        max_val = data[metric].max()
        data_norm[f'{metric}_norm'] = (data[metric] - min_val) / (max_val - min_val)

# Crear un gráfico para cada valor de alfa
alpha_values = sorted(data['alpha'].unique())
metric_names = ['Coherencia Curricular', 'Coincidencia Promedio',
                'Estudiantes No Afectados', 'Coherencia de Previas']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
markers = ['o', 's', '^', 'D']

for alpha_val in alpha_values:
    plt.figure(figsize=(10, 6))

    # Filtrar los datos para este valor de alfa
    alpha_data = data_norm[data_norm['alpha'] == alpha_val].sort_values('beta')

    # Graficar cada métrica
    for i, metric in enumerate(metrics):
        plt.plot(alpha_data['beta'], alpha_data[f'{metric}_norm'],
                 color=colors[i], marker=markers[i], linewidth=2, markersize=8,
                 label=metric_names[i])

    # Configurar el gráfico
    plt.xlabel('Valor de β', fontsize=12)
    plt.ylabel('Valor Normalizado', fontsize=12)
    plt.title(f'Métricas de Rendimiento para α = {alpha_val}', fontsize=14, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks([0, 0.25, 0.5, 0.75, 1])
    plt.ylim(0, 1.05)

    # Añadir leyenda
    plt.legend(loc='best', fontsize=10)

    plt.tight_layout()
    plt.savefig(f'metricas_alpha_{int(alpha_val*100)}.png', dpi=300, bbox_inches='tight')
    plt.close()  # Cerrar la figura explícitamente

    print(f"Gráfico para α = {alpha_val} generado correctamente.")

# Crear también una versión con valores originales (no normalizados)
for alpha_val in alpha_values:
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Filtrar los datos para este valor de alfa
    alpha_data = data[data['alpha'] == alpha_val].sort_values('beta')

    # Usar dos ejes Y diferentes para manejar las escalas
    ax1.set_xlabel('Valor de β', fontsize=12)
    ax1.set_ylabel('Coherencia y Coincidencia', fontsize=12, color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Graficar las métricas de coherencia y coincidencia
    line1, = ax1.plot(alpha_data['beta'], alpha_data['m_curricula'],
                      'o-', color='tab:blue', linewidth=2, markersize=8,
                      label='Coherencia Curricular')
    line2, = ax1.plot(alpha_data['beta'], alpha_data['m_coincidencia'],
                      's--', color='tab:cyan', linewidth=2, markersize=8,
                      label='Coincidencia Promedio')

    # Crear un segundo eje Y para estudiantes afectados
    ax2 = ax1.twinx()
    ax2.set_ylabel('Estudiantes Afectados', fontsize=12, color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    line3, = ax2.plot(alpha_data['beta'], alpha_data['m_estudiantes'],
                      '^-', color='tab:red', linewidth=2, markersize=8,
                      label='Estudiantes Afectados')

    # Crear un tercer eje Y para coherencia de previas
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))  # Desplazar el eje a la derecha
    ax3.set_ylabel('Coherencia de Previas', fontsize=12, color='tab:green')
    ax3.tick_params(axis='y', labelcolor='tab:green')

    line4, = ax3.plot(alpha_data['beta'], alpha_data['m_previas'],
                      'D-', color='tab:green', linewidth=2, markersize=8,
                      label='Coherencia de Previas')

    # Configurar el gráfico
    plt.title(f'Métricas de Rendimiento para α = {alpha_val} (Valores Originales)',
              fontsize=14, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks([0, 0.25, 0.5, 0.75, 1])

    # Combinar las leyendas de los tres ejes
    lines = [line1, line2, line3, line4]
    labels = [line.get_label() for line in lines]
    plt.legend(lines, labels, loc='best', fontsize=10)

    plt.tight_layout()
    plt.savefig(f'metricas_originales_alpha_{int(alpha_val*100)}.png', dpi=300, bbox_inches='tight')
    plt.close(fig)  # Cerrar la figura explícitamente

    print(f"Gráfico con valores originales para α = {alpha_val} generado correctamente.")

print("Todos los gráficos han sido generados.")
