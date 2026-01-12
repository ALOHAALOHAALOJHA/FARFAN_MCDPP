#!/bin/bash
PR_NUM=$1

if [ -z "$PR_NUM" ]; then
  echo "Uso: ./verificar_pr.sh <numero_de_pr>"
  exit 1
fi

echo "=== VERIFICANDO PR #$PR_NUM ==="
echo ""

# Buscar el merge commit del PR
MERGE_COMMIT=$(git log --oneline --grep="Merge pull request #$PR_NUM" --format="%H" | head -1)

if [ -z "$MERGE_COMMIT" ]; then
  echo "❌ PR #$PR_NUM no encontrado en el historial"
  exit 1
fi

echo "✅ PR encontrado en commit: $MERGE_COMMIT"
git log -1 --format="   Fecha: %ci%n   Mensaje: %s" $MERGE_COMMIT
echo ""

# Obtener la rama que se fusionó
BRANCH=$(git log -1 --format="%s" $MERGE_COMMIT | grep -oP 'from .*/\K.*')
echo "📌 Rama fusionada: $BRANCH"
echo ""

# Verificar si fue un merge con -s ours (sin código real)
PARENT1=$(git rev-parse ${MERGE_COMMIT}^1 2>/dev/null)
PARENT2=$(git rev-parse ${MERGE_COMMIT}^2 2>/dev/null)

if [ -n "$PARENT2" ]; then
  # Comparar el árbol del merge con cada padre
  TREE_MERGE=$(git rev-parse ${MERGE_COMMIT}^{tree})
  TREE_P1=$(git rev-parse ${PARENT1}^{tree})
  TREE_P2=$(git rev-parse ${PARENT2}^{tree})
  
  if [ "$TREE_MERGE" = "$TREE_P1" ]; then
    echo "⚠️  MERGE STRATEGY: -s ours (SE DESCARTÓ EL CÓDIGO DE LA RAMA)"
    echo ""
    echo "Código que estaba en la rama pero NO se fusionó:"
    git diff --stat $PARENT1..$PARENT2 | head -20
  elif [ "$TREE_MERGE" = "$TREE_P2" ]; then
    echo "⚠️  MERGE STRATEGY: -s theirs (SE REEMPLAZÓ TODO CON LA RAMA)"
  else
    echo "✅ MERGE NORMAL: El código de la rama SÍ se fusionó"
    echo ""
    echo "Cambios incluidos en el merge:"
    git diff --stat $PARENT1..$MERGE_COMMIT | head -20
  fi
else
  echo "ℹ️  Fast-forward merge o commit directo"
fi

echo ""
echo "=== VERIFICACIÓN EN MAIN ACTUAL ==="

# Verificar si los archivos del PR existen actualmente
if [ -n "$PARENT2" ]; then
  FILES_IN_PR=$(git diff --name-only $PARENT1..$PARENT2 | head -5)
  echo "Archivos que estaban en el PR:"
  echo "$FILES_IN_PR" | while read file; do
    if [ -f "$file" ]; then
      echo "  ✅ $file (existe en main)"
    else
      echo "  ❌ $file (NO existe en main)"
    fi
  done
fi

