const { createApp } = Vue
import Step from './Step.js'
import { load_step_list } from './utils.js'

load_step_list(function(step_list) {
    // Ideally we should have a better way of doing this
    window.step_list = step_list

    createApp({
        components: {
            Step
        },
        methods: {
            stepUpdate(event, index) {
                this.steps[index]["step"] = event.target.value
                this.steps[index]["arguments"] = {}
            },
            addToEnd() {
                this.addStep(this.steps.length)
            },
            addStep(index) {
                this.steps.splice(index+1, 0, {
                    "step": "para_cada",
                    "depth": 1,
                    "arguments": {}
                })
            },
            unindentStep(index) {
                if (this.steps[index].depth > 1)
                    this.steps[index].depth--
            },
            indentStep(index) {
                this.steps[index].depth++
            },
            moveStepUp(index) {
                if (index > 0) {
                    let tmp = this.steps[index-1]
                    this.steps[index-1] = this.steps[index]
                    this.steps[index] = tmp
                }
            },
            moveStepDown(index) {
                if (index < this.steps.length - 1) {
                    let tmp = this.steps[index+1]
                    this.steps[index+1] = this.steps[index]
                    this.steps[index] = tmp
                }
            },
            duplicateStep(index) {
                this.steps.splice(index, 0, {...this.steps[index]})
            },
            removeStep(index) {
                this.steps.splice(index, 1)
            },
            stepParameterChange(event, index, paramName) {
                this.steps[index]['arguments'][paramName] = event.target.value
            },
            stepParameterAdd(index, paramName, value) {
                this.steps[index]['arguments'][paramName] = value
            },
            stepParameterDelete(index, paramName) {
                delete this.steps[index]['arguments'][paramName]
            }
        },
        data() {
            return {
                steps: [{
                    "step": "screenshot",
                    "depth": 1,
                    "arguments":{}
                },
                {
                    "step": "espere",
                    "depth": 2,
                    "arguments": {
                        "segundos": "10"
                    }
                }]
            }
        }
    }).mount("#dynamic-processing-steps")
})
