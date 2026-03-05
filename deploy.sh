#!/bin/bash

# Скрипт автоматического деплоя с тестированием

echo "=========================================="
echo "🚀 Автоматический деплой с тестами"
echo "=========================================="
echo ""

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Максимальное количество попыток
MAX_ATTEMPTS=3
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "📝 Попытка $ATTEMPT из $MAX_ATTEMPTS"
    echo ""
    
    # Запускаем тесты
    bash run_tests.sh
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Тесты пройдены! Начинаем деплой..."
        echo ""
        
        # Проверяем что есть изменения
        if git diff --quiet && git diff --cached --quiet; then
            echo "ℹ️  Нет изменений для коммита"
            echo ""
            
            # Пушим если есть непушенные коммиты
            if [ -n "$(git log @{u}.. 2>/dev/null)" ]; then
                echo "📤 Пушим существующие коммиты..."
                git push
                
                if [ $? -eq 0 ]; then
                    echo ""
                    echo "=========================================="
                    echo "✅ Деплой успешен!"
                    echo "=========================================="
                    echo ""
                    echo "🎉 Railway автоматически задеплоит изменения"
                    echo "⏱️  Ожидайте 60-90 секунд"
                    exit 0
                else
                    echo "❌ Ошибка при пуше"
                    exit 1
                fi
            else
                echo "✅ Всё уже задеплоено!"
                exit 0
            fi
        else
            # Есть изменения - коммитим
            echo "📝 Добавляем изменения..."
            git add .
            
            # Генерируем сообщение коммита
            COMMIT_MSG="Auto-deploy: $(date '+%Y-%m-%d %H:%M:%S')"
            
            echo "💾 Коммитим: $COMMIT_MSG"
            git commit -m "$COMMIT_MSG"
            
            if [ $? -eq 0 ]; then
                echo "📤 Пушим на GitHub..."
                git push
                
                if [ $? -eq 0 ]; then
                    echo ""
                    echo "=========================================="
                    echo "✅ Деплой успешен!"
                    echo "=========================================="
                    echo ""
                    echo "🎉 Railway автоматически задеплоит изменения"
                    echo "⏱️  Ожидайте 60-90 секунд"
                    exit 0
                else
                    echo "❌ Ошибка при пуше"
                    ATTEMPT=$((ATTEMPT + 1))
                    
                    if [ $ATTEMPT -le $MAX_ATTEMPTS ]; then
                        echo "🔄 Повторная попытка через 5 секунд..."
                        sleep 5
                    fi
                fi
            else
                echo "❌ Ошибка при коммите"
                exit 1
            fi
        fi
    else
        echo ""
        echo "❌ Тесты провалились на попытке $ATTEMPT"
        echo ""
        
        ATTEMPT=$((ATTEMPT + 1))
        
        if [ $ATTEMPT -le $MAX_ATTEMPTS ]; then
            echo "🔄 Повторный запуск тестов через 3 секунды..."
            echo ""
            sleep 3
        fi
    fi
done

echo ""
echo "=========================================="
echo "❌ Деплой не удался после $MAX_ATTEMPTS попыток"
echo "=========================================="
echo ""
echo "⚠️  Проверьте ошибки тестов и исправьте код"
exit 1
