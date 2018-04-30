<template>
    <div>
        <h1>Active Downloads</h1>
        <el-button v-loading="is_scanning" v-on:click="triggerscan">Scan Now</el-button>

        <p>Active Items</p>
        <download-table
            :filter="active_filter"
            />
        
        <p>Pending Items</p>
        <download-table
            :filter="new_filter"
            />
    </div>
</template>

<script>
import moment from 'moment'

export default {
    data() {
        return {
            active_filter: {
                status: 'in_progress'
            },
            new_filter: {
                status: 'new'
            },
            is_scanning: false
        }
    },
    computed: {
    },
    methods: {
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
    }
}
</script>

<style scoped>
.magnet_input {
    margin-bottom: 10px;
}
</style>
