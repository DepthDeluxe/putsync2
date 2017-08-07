<template>
    <div>
        <h1>Home</h1>
        <p>Latest completed downloads:</p>
        <download-history-table></download-history-table>

        <p class="notice">Last scanned: {{ time_last_scanned }}</p>
    </div>
</template>

<script>
export default {
    data () {
        return {
            time_last_scanned: '???'
        }
    },
    methods: {
    }
}
</script>

<style scoped>
p.notice {
    margin-top: 35px;
    font-size: 10pt;
}
</style>
