<script lang="ts" setup>
const enum ImageTypes {
    BEFORE = 'before',
    AFTER = 'after',
    IDEAL = 'ideal'
}

const props = defineProps({
    imageUrl: {
        type: String,
        required: true
    },
    showImageType: {
        type: String,
        default: ImageTypes.BEFORE
    }
})
</script>

<template>
    <div class="image-block">
        <div v-if="showImageType === ImageTypes.BEFORE" class="message">現在のあなた</div>
        <div v-else-if="showImageType === ImageTypes.AFTER" class="message after">将来のあなた</div>
        <div v-else-if="showImageType === ImageTypes.IDEAL" class="message after">理想のあなた</div>
        <div class="image-frame">
            <img :src="imageUrl" alt="Image" class="image" />
        </div>
    </div>
</template>

<style scoped>
.image-block {
    display: flex;
    flex-direction: column;
    text-align: center;
    margin-bottom: 20px;
}

.message {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 10px;
    line-height: 2.0rem;
}

.after {
    font-size: 2.0rem;
    line-height: 2.0rem;
}

.image-frame {
    border: 2px solid #ccc;
    border-radius: 8px;
    overflow: hidden;
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
    height: max-content;
}

.image {
    display: block;
    width: 100%;
    height: auto;
}
</style>