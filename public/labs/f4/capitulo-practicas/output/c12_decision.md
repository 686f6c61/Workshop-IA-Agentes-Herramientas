# Práctica F4 C12

Estado: `valid`.

Text-to-SQL requiere validación antes de ejecutar.

## Qué te llevas

Una consulta Text-to-SQL validada antes de ejecutarse.

## Evidencia

```json
{
  "status": "valid",
  "summary": "Text-to-SQL requiere validación antes de ejecutar.",
  "sql": "SELECT campus, SUM(importe) AS total FROM pagos WHERE estado='pendiente' GROUP BY campus ORDER BY total DESC LIMIT 3",
  "rows": [
    {
      "campus": "Norte",
      "total": 800.0
    },
    {
      "campus": "Sur",
      "total": 120.0
    }
  ],
  "what_you_take": "Una consulta Text-to-SQL validada antes de ejecutarse."
}
```
