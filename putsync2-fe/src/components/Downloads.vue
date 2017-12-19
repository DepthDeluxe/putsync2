<template>
    <div>
        <h1>Active Downloads</h1>
        <el-button v-loading="is_scanning" v-on:click="triggerscan">Scan Now</el-button>

        <p>Items actively downloading</p>
        <el-table
            v-loading="table_loading"
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
            table_loading: false,
            table_update_interval_id: null,
            table_data: [],
            is_scanning: false
        }
    },
    computed: {
    },
    methods: {
        gettabledata() {
            this.table_loading = true

            return this.$http.get('/api/downloads?status=in_progress').then(response => {
                this.table_data = response.body.data
            }).then(() => {
                this.table_loading = false
            })
        },
        triggerscan() {
            if (this.is_scanning) {
                return
            }

            this.is_scanning = true
            this.$message('Scan started')

            this.$http.post('/api/full').then(response => {
                this.is_scanning = false
                this.$message({
                    message: 'Scan completed',
                    type: 'success'
                })
                console.log(response)
            }, response => {
                this.is_scanning = false
                this.$message({
                    message: 'Scanning failed',
                    type: 'error'
                })
            })
        }
    },
    mounted() {
        this.gettabledata()

        this.table_update_interval_id = setInterval(this.gettabledata, 2500)
    },
    beforeDestroy() {
        clearInterval(this.table_update_interval_id)
    }
}
</script>

<style scoped>
.magnet_input {
    margin-bottom: 10px;
}
</style>
