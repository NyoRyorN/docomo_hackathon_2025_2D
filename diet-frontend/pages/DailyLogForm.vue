<script setup>
    // bootstrap import部分
import { useHead } from '#app'
import { useFetch } from '#app'
import { navigateTo } from '#app'
    useHead({
        link: [
            {
            rel: 'stylesheet',
            href: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'
            }
        ],
        script: [
            {
            src: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
            defer: true
            }
        ],
        // 背景画像
        script: [
            {
                src: 'https://cdnjs.cloudflare.com/ajax/libs/trianglify/2.0.0/trianglify.min.js',
                defer: true
            }
        ],
    })

    import { reactive, ref } from "vue"

const form = reactive({
        weight: "",
        exercise_time: "",
        sleep_time: "",
    })

    const previewUrl = ref(null)
    const isLoading = ref(false)

    function handleFileUpload(event) {
    const file = event.target.files[0]
    if (file) {
        form.picture = file
        previewUrl.value = URL.createObjectURL(file)
    }
    }

async function handleSubmit() {
    try {
        // 画像が選択されているかチェック
        if (!form.picture) {
            alert('画像を選択してください')
            return
        }

        isLoading.value = true

        // FormDataを作成してファイルとフォームデータを送信
        const formData = new FormData()
        formData.append('meal_image', form.picture)
        formData.append('face_image', form.picture) // 現在は同じ画像を使用
        formData.append('user_id', 'user_123') // 適宜ユーザーIDを設定
        formData.append('session_id', `session_${Date.now()}`) // セッションIDを生成
        
        // 追加のフォームデータ
        // 追加のフォームデータ
        formData.append('weight', form.weight)
        formData.append('exercise_time', form.exercise_time)
        formData.append('sleep_time', form.sleep_time)

        console.log('Sending request to API...')
        
        try {
            // 本番のAPI呼び出し
            const response = await $fetch('http://127.0.0.1:8000/generate-answer', {
                method: 'POST',
                body: formData
            })
            
            // 成功時の処理
            console.log('API Response:', response)
            alert('解析が完了しました！')
            
            // 結果画面に遷移
            await navigateToNext(response)
            
        } catch (apiError) {
            // APIが利用できない場合はダミーデータで続行
            console.warn('API呼び出しに失敗しました。ダミーデータで続行します:', apiError)
            
            const dummyResponse = {
                answer: "ダミーの解析結果です",
                meta: {
                    user_id: "user_123",
                    weight: form.weight,
                    exercise_time: form.exercise_time,
                    sleep_time: form.sleep_time
                }
            }
            
            console.log('Using dummy response:', dummyResponse)
            alert('解析が完了しました！（ダミーデータ）')
            
            // 結果画面に遷移
            await navigateToNext(dummyResponse)
        }
        
    } catch (err) {
        console.error('Request failed:', err)
        
        // より詳細なエラー情報を表示
        let errorMessage = 'リクエストに失敗しました'
        if (err.response) {
            console.error('Response status:', err.response.status)
            console.error('Response data:', err.response._data)
            errorMessage = `サーバーエラー (${err.response.status}): ${err.response._data?.detail || err.response.statusText}`
        } else if (err.message) {
            errorMessage = err.message
        }
        
        alert(errorMessage)
    } finally {
        isLoading.value = false
    }
}

    // 背景画像
    import { onMounted, onUnmounted, nextTick } from "vue";
    function drawBackground() {
        const target = document.getElementById("background");
        if (!target) return;

        // 前回のSVGを削除
        target.innerHTML = "";

        const rect = target.getBoundingClientRect();
        const width = rect.width || 1;
        const height = rect.height || 1;

        const pattern = window.Trianglify({
            width,
            height,
            cell_size: 100,
            x_colors: "Blues",
            y_colors: "Blues",
        });

        target.appendChild(pattern.svg());
    }
    onMounted(async () => {
        await nextTick();
        // 初回描画
        drawBackground();
        // リサイズ時にも描画
        window.addEventListener("resize", drawBackground);
    });
    onUnmounted(() => {
        window.removeEventListener("resize", drawBackground);
    });

    // 画面遷移
    const navigateToNext = async (response) => {
        // レスポンスデータをセッションストレージに保存
        if (response) {
            sessionStorage.setItem('apiResponse', JSON.stringify(response))
        }
        
        // Nuxt.jsのnavigateTo を使用してページ遷移
        await navigateTo('/ResultsPage')
    }
</script>

<template>
    <div class="container">
        <ClientOnly>
            <div id="background" style="width: 100%; height: 100vh; position: fixed; top: 0; left: 0; z-index: -1;"></div>
        </ClientOnly>
        <div class="card mx-auto my-5 shadow-lg w-75" style="width: 75%;">
            <div class="card-body">    
                <h3 class="card-title text-center">
                    今日のことを教えてください
                </h3>
                <form @submit.prevent="handleSubmit">
                    <div class="row align-items-stretch">
                        <!-- 左側: 写真アップロード -->
                        <div class="form-group col-md-6 d-flex flex-column">
                            <label for="meal-picture" class="mb-2 fs-3">
                                今日のご飯
                            </label>
                            <small class="form-text text-muted mb-3">
                                今日食べたご飯の写真をアップロードしてください
                            </small>
                            <input
                                id="meal-picture"
                                type="file"
                                class="form-control mb-3"
                                accept="image/*"
                                @change="handleFileUpload"
                                required
                            />

                            <!-- プレビュー領域 -->
                            <div class="preview-field d-flex justify-content-center align-items-center border" style="height: 500px; overflow: hidden;">
                                <div v-if="previewUrl" class="d-flex justify-content-center align-items-center w-100 h-100">
                                    <img
                                        :src="previewUrl"
                                        alt="preview"
                                        class="img-thumbnail"
                                        style="height: 100%; width: auto; object-fit: contain;"
                                    />
                                </div>
                                <div v-else class="text-muted text-center">
                                    画像がここに表示されます
                                </div>
                            </div>

                        </div>

                        <!-- 右側: 入力フォーム -->
                        <div class="col-md-6 pt-5 pb-3 d-flex flex-column">
                            <div class="form-group my-3">
                                <label for="user-weight">今日の体重</label>
                                <div class="input-group">
                                    <input
                                        id="user-weight"
                                        class="form-control"
                                        type="text"
                                        placeholder="今日の体重を入力してください"
                                        v-model="form.weight"
                                        required
                                    />
                                    <span class="input-group-text">kg</span>
                                </div>
                            </div>

                            <div class="form-group my-3">
                            <label for="exercise-time">運動習慣</label>
                                <div class="input-group">
                                    <input
                                        id="exercise-time"
                                        class="form-control"
                                        type="number"
                                        min="0"
                                        max="24"
                                        placeholder="今日の運動時間を入力してください"
                                        v-model="form.exercise_time"
                                        required
                                    />
                                    <span class="input-group-text">時間</span>
                                </div>
                            </div>


                            <div class="form-group my-3">
                                <label for="sleep-time">睡眠時間</label>
                                <div class="input-group">
                                    <input
                                        id="sleep-time"
                                        class="form-control"
                                        type="number"
                                        min="0"
                                        max="24"
                                        placeholder="昨日の睡眠時間を入力してください"
                                        v-model="form.sleep_time"
                                        required
                                    />
                                    <span class="input-group-text">時間</span>
                                </div>
                            </div>
                        </div>
                    </div>

            
                    <!-- ボタン -->
                    <div class="row mt-3 mx-auto">
                        <button 
                            type="submit" 
                            class="btn btn-primary w-50 mx-auto fs-4"
                            :disabled="isLoading"
                        >
                            <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                            {{ isLoading ? '解析中...' : '未来の自分を見る' }}
                        </button>
                    </div>
                </form>
        
                <!-- デバッグ -->
                <pre>{{ form }}</pre>
            </div>
        </div>
    </div>
</template>

<style lang="css" scoped>
    .form-group:has(input:required) > label::after {
        content: " *";
        color: red;
        margin-left: 2px;
    }
</style>