import Parameter from './Parameter.js'

import { param_to_placeholder } from './utils.js'

export default {
    props: ['step', 'depth', 'arguments', 'index', 'inner_step',
        'inner_arguments'],
    components: {
        Parameter
    },
    computed: {
        indentationMargin() {
            return (this.depth * 2 - 2) + "em"
        },

        // Step definition data
        allowedSteps() {
            return window.step_list
        },
        stepDefinition() {
            return window.step_list.filter(entry => {
                return entry.name === this.step
            })[0]
        },
        mandatoryParams() {
            return this.stepDefinition["mandatory_params"]
        },
        optionalParams() {
            return this.stepDefinition["optional_params"]
        },
        usedOptionalParams() {
            return this.stepDefinition["optional_params"].filter(
                x => Object.keys(this.arguments).includes(x)
            )
        },
        unusedOptionalParams() {
            return this.stepDefinition["optional_params"].filter(
                x => !Object.keys(this.arguments).includes(x)
            )
        },
        placeholder() {
            return param_to_placeholder(this.step)
        },

        // Inner step definition data
        innerStepType() {
            if ("inner_step" in this.stepDefinition)
                return this.stepDefinition["inner_step"]
            return false
        },
        innerAllowedSteps() {
            // TODO Filter
            return window.step_list
        },
        innerStepDefinition() {
            return window.step_list.filter(entry => {
                return entry.name === this.inner_step
            })[0]
        },
        innerMandatoryParams() {
            return this.innerStepDefinition["mandatory_params"]
        },
        innerOptionalParams() {
            return this.innerStepDefinition["optional_params"]
        },
        innerUsedOptionalParams() {
            return this.innerStepDefinition["optional_params"].filter(
                x => Object.keys(this.inner_arguments).includes(x)
            )
        },
        innerUnusedOptionalParams() {
            return this.innerStepDefinition["optional_params"].filter(
                x => !Object.keys(this.inner_arguments).includes(x)
            )
        },
        innerPlaceholder() {
            return param_to_placeholder(this.inner_step)
        },

    },
    methods: {
        getParameterValue(param) {
            if (param in this.arguments)
                return this.arguments[param]
            return ""
        },
        getParameterPlaceholder(param) {
            return param_to_placeholder(param)
        },
        getParameterFieldOptions(param) {
            if ('field_options' in this.stepDefinition)
                return this.stepDefinition['field_options'][param]
            return null
        },
        emitStepAdd(param) {
            let defaultVal = ""

            let fieldOpts = this.getParameterFieldOptions(param)
            if (fieldOpts && 'default_value' in fieldOpts) {
                defaultVal = fieldOpts['default_value']
            }

            this.$emit('step-parameter-add', this.index, param, defaultVal)
        }
    },
    template: `
    <div class="card step-block" v-bind:style="{ left: indentationMargin }"
        style="min-height: 100px">
        <!-- Auxiliary buttons (add, indent, move, duplicate, delete) -->
        <div class="row block-controller-interface">
            <div class="col-sm" @click="$emit('add-step', index)">
                <img class="block-controller-button" src="/static/icons/black-plus.svg">
            </div>
            <div class="col-sm" @click="$emit('unindent-step', index)" v-show="depth > 1">
                <img class="block-controller-button" src="/static/icons/arrow-left-black.svg">
            </div>
            <div class="col-sm" @click="$emit('indent-step', index)">
                <img class="block-controller-button" src="/static/icons/arrow-right-black.svg">
            </div>
            <div class="col-sm" @click="$emit('move-step-up', index)" v-show="index > 0">
                <img class="block-controller-button" src="/static/icons/arrow-up-black.svg">
            </div>
            <div class="col-sm" @click="$emit('move-step-down', index)">
                <img class="block-controller-button" src="/static/icons/arrow-down-black.svg">
            </div>
            <div class="col-sm" @click="$emit('duplicate-step', index)">
                <img class="block-controller-button" src="/static/icons/duplicate-black.svg">
            </div>
            <div class="col-sm" @click="$emit('remove-step', index)">
                <img class="block-controller-button" src="/static/icons/black-x.svg">
            </div>
        </div>

        <!-- Step details -->
        <div style="display: flex; flex-wrap: wrap">
            <div class="step-config-select">
                <select class="row form-control select-step" :value="step"
                    @change="$emit('step-update', $event, index)">
                    <option v-for="choice in allowedSteps" :value="choice.name">
                        {{ choice.name_display }}
                    </option>
                </select>
            </div>

            <Parameter v-for="param in mandatoryParams"
                :name="param"
                :displayName="getParameterPlaceholder(param)"
                :fieldOptions="getParameterFieldOptions(param)"
                :value="getParameterValue(param)"
                @parameter-change="$emit('step-parameter-change', $event,
                    index, param)"
            ></Parameter>

            <div style="border-radius: 1em; padding-right: 1em;
                margin-left: auto;" v-if="unusedOptionalParams.length > 0">
                <button type="button" class="btn btn-primary"
                    data-toggle="dropdown" aria-haspopup="true"
                    aria-expanded="false">
                    <img src="/static/icons/white-plus-icon.svg"
                        style="width: 1em; height: 1em;">
                </button>
                <div class="dropdown-menu">
                    <a v-for="param in unusedOptionalParams" class="dropdown-item"
                        style="cursor:pointer"
                        :data-param="param"
                        @click="emitStepAdd(param)">
                        {{getParameterPlaceholder(param)}}
                    </a>
                </div>
            </div>

            <hr style="width:100%" />

            <div style="padding-left: 1em; width: 100%">
                <Parameter v-for="param in usedOptionalParams"
                    optional
                    :name="param"
                    :displayName="getParameterPlaceholder(param)"
                    :fieldOptions="getParameterFieldOptions(param)"
                    :value="getParameterValue(param)"
                    @parameter-change="$emit('step-parameter-change', $event,
                        index, param)"
                    @parameter-delete="$emit('step-parameter-delete', index,
                        param)"
                    style="margin-bottom: 1em"
                ></Parameter>
            </div>
        </div>
        <div v-text="index"></div>
        <div v-text="step"></div>
        <div v-text="depth"></div>
        <div v-text="arguments"></div>
        <div v-text="mandatoryParams"></div>
        <div v-text="optionalParams"></div>
        <div v-text="this.stepDefinition['field_options']"></div>
    </div>
    `
}
