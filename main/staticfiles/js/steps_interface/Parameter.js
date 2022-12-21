export default {
    props: { 'name': {}, 'displayName': {}, 'fieldOptions': {}, 'value': {},
        'optional': {
            default: false,
            type: Boolean
        }
    },
    computed: {
        fieldType() {
            console.log(this.fieldOptions)
            if (!this.fieldOptions || !('field_type' in this.fieldOptions))
                return 'text'
            return this.fieldOptions['field_type']
        },
        placeholder() {
            if (this.fieldOptions && 'input_placeholder' in this.fieldOptions)
                return this.fieldOptions['input_placeholder']
            return displayName
        },
        checkboxLabel() {
            if (this.fieldType === 'checkbox')
                return this.fieldOptions['checkbox_label']
            return ''
        },
        selectOptions() {
            if (this.fieldType === 'select')
                return this.fieldOptions['select_options']
            return []
        }
    },
    template: `
    <div class="col-sm">
        {{fieldType}}
        <!-- Close button (if optional parameter) -->
        <a style="position: absolute; top: -0.75em; right: 1.2em;
            cursor: pointer;" v-if="optional"
            @click="$emit('parameter-delete')">
            <img src="/static/icons/black-x.svg">
        </a>


        <!-- Text/number input -->
        <input v-if="fieldType === 'text' || fieldType === 'number'"
            @change="$emit('parameter-change', $event, name)" :type="fieldType"
            :placeholder="displayName" class="row form-control"
            :data-param="name" data-type="text" :value="value" />

        <!-- Checkbox input -->
        <input v-if="fieldType === 'checkbox'"
            @change="$emit('parameter-change', $event, name)" :type="fieldType"
            :id="name" class="form-check-input"
            :data-param="name" data-type="bool" :checked="value" />
        <label v-if="fieldType === 'checkbox'" :for="name"
            class="form-check-label">{{checkboxLabel}}</label>

        <!-- Select input -->
        <select v-if="fieldType === 'select'"
            @change="$emit('parameter-change', $event, name)"
            class="row form-control" :id="name" :data-param="name"
            data-type="text">
            <option value="" disabled :selected="!value">
                {{displayName}}
            </option>
            <option v-for="option in selectOptions" :value="option"
                :selected="value == option">
                {{option}}
            </option>
        </select>

    </div>
    `
}
