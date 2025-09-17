<template>
    <div class="card mx-auto my-5" style="width: 75%;">
        <div class="card-body">    
            <h3 class="card-title text-center">
                今日のあなたのことを教えてください
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
                    <button type="submit" class="btn btn-primary w-50 mx-auto fs-4">
                        未来の自分を見る
                    </button>
                </div>
            </form>
    
            <!-- デバッグ -->
            <pre>{{ form }}</pre>
        </div>
    </div>
    
</template>

<script setup>
    // bootstrap import部分
    import { useHead } from '#app'
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
        ]
    })

    import { reactive, ref } from "vue"

    const form = reactive({
        weight: "",
        exercise_time: "",
        sleep_time: "",
    })

    const previewUrl = ref(null)

    function handleFileUpload(event) {
    const file = event.target.files[0]
    if (file) {
        form.picture = file
        previewUrl.value = URL.createObjectURL(file)
    }
    }

    function handleSubmit() {
        alert(`今日の体重: ${form.weight}kg\n運動時間: ${form.exercise_time}時間\n昨日の睡眠時間: ${form.sleep_time}`)
    }

</script>

<style lang="css" scoped>
    .form-group:has(input:required) > label::after {
        content: " *";
        color: red;
        margin-left: 2px;
    }
</style>