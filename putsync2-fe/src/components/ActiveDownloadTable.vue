<template>
    <div>
        <el-table
            :data="table_data"
            style="width: 100%"
            height=500
            stripe
            border>
            <el-table-column prop="filepath" label="Name"></el-table-column>
            <el-table-column prop="started_at" label="Started At"></el-table-column>
            <el-table-column prop="running_for" label="Running For"></el-table-column>
        </el-table>
    </div>
</template>

<script>
export default {
    data() {
        return {
            table_data: []
        }
    },
    mounted() {
        this.gettabledata()

        setInterval(this.gettabledata, 2500)
    },
    methods: {
        gettabledata() {
            return this.$http.get('/api/downloads?status=in_progress').then(response => {
                this.table_data = response.body.data
            })
        }
    }
}
</script>

<style scoped>
</style>
