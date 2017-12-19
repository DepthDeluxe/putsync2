<template>
    <div>
        <h1>Add Magnet Link</h1>
        <p>
            Paste the magnet link from the torrenting website.  Once submitted
            it will be sent to put.io where putsync2 will pick it up.
        </p>
        <el-form>
            <el-form-item label="Magnet Link">
                <el-input type="textarea" :autosize="{ minRows: 2, maxRows: 5 }" placeholder="Magnet link" v-model="magnet_link" class="magnet_input"></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" :disabled="is_submit_disabled" v-on:click="submit">Submit</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
export default {
    data() {
        return {
            magnet_link: '',
        }
    },
    computed: {
        is_submit_disabled() {
            return !this.validate()
        }
    },
    methods: {
        submit() {
            if (this.validate() == false) {
                return
            }

            this.$http.post('/api/add', { magnet_link: this.magnet_link }).then(response => {
                this.$message('Added to put.io')
                this.magnet_link = ''
                console.log(response)
            });
        },
        validate() {
            if (this.magnet_link.length == 0) {
                return false
            }
            if (this.magnet_link.match(/magnet:\?xt=/) == null) {
                return false
            }
            return true
        }
    }
}
</script>

<style scoped>
.magnet_input {
    margin-bottom: 10px;
}
</style>
