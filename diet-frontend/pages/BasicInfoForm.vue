<template>
    <div class="card mx-auto my-5" style="width: 75%;">
        <div class="card-body">    
            <h3 class="card-title text-center">
                あなたのことを教えてください
            </h3>
            <form @submit.prevent="handleSubmit">
                <div class="row align-items-stretch">
                    <!-- 左側: 写真アップロード -->
                    <div class="col-md-6 d-flex flex-column">
                        <label for="user-picture" class="mb-2">現在のあなた</label>
                        <small class="form-text text-muted mb-3">
                            あなたの正面から見た顔の画像を選択してください
                        </small>
                        <input
                        id="user-picture"
                        type="file"
                        class="form-control mb-3"
                        @change="handleFileUpload"
                        />

                        <!-- プレビュー領域 -->
                        <div class="preview-field flex-grow-1 d-flex justify-content-center align-items-center border" style="min-height: 500px;">
                        <div v-if="previewUrl">
                            <img
                            :src="previewUrl"
                            alt="preview"
                            class="img-thumbnail"
                            style="max-width: 100%; max-height: 100%;"
                            />
                        </div>
                        <div v-else class="text-muted text-center">
                            画像がここに表示されます
                        </div>
                        </div>
                    </div>

                    <!-- 右側: 入力フォーム -->
                    <div class="col-md-6 d-flex flex-column">
                        <div class="form-group my-2 flex-fill">
                        <label for="user-name">名前</label>
                        <input
                            id="user-name"
                            class="form-control"
                            type="text"
                            placeholder="名前を入力"
                            v-model="form.name"
                        />
                        </div>

                        <div class="form-group my-2 flex-fill">
                        <label for="user-height">身長</label>
                        <input
                            id="user-height"
                            class="form-control"
                            type="number"
                            placeholder="身長を入力"
                            v-model="form.height"
                        />
                        </div>

                        <div class="form-group my-2 flex-fill">
                        <label for="user-age">年齢</label>
                        <input
                            id="user-age"
                            class="form-control"
                            type="number"
                            placeholder="年齢を入力"
                            v-model="form.age"
                        />
                        </div>

                        <div class="form-group my-2 flex-fill">
                        <label for="gender">性別</label>
                        <select id="gender" class="form-select" v-model="form.gender">
                            <option disabled value="">選択してください</option>
                            <option value="male">男性</option>
                            <option value="female">女性</option>
                            <option value="none">秘密</option>
                        </select>
                        </div>

                        <div class="form-group my-2 flex-fill">
                        <label for="user-weight-ideal">理想の体重</label>
                        <input
                            id="user-weight-ideal"
                            class="form-control"
                            type="number"
                            placeholder="目指す体重を入力"
                            v-model="form.weight"
                        />
                        </div>
                    </div>
                </div>

        
                <!-- ボタン -->
                <div class="row mt-3 mx-auto">
                    <button type="submit" class="btn btn-primary w-50 mx-auto fs-4">
                        更新・登録
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
        name: "",
        height: "",
        age: "",
        gender: "",
        picture: null,
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
    alert(`お名前: ${form.name}\n身長: ${form.height}\n年齢: ${form.age}\n写真: ${form.picture?.name || "なし"}`)
    }

</script>
