/*
jQuery widget to manage formsets used by Django on the front-end
*/

(function($) {
    $.widget('mp.formset', {
        options: {
            prefix: 'form',
            templateId: 'formset-subform-template',
            subformSelector: '.formset-subform',
            displayControls: true,
            addBtnContent: $('<a class="fa fa-plus"></a>'),
            rmBtnContent: $('<a class="fa fa-trash"></a>'),
            addBtnClass: '',
            rmBtnClass: '',
        },

        _insertDeleteBtn: function(el) {
            /**
             * Inserts a delete button which removes the supplied subform
             * @param  {Node} el [The subform to receive the delete button]
             */
            let btn = $(this.options.rmBtnContent).clone(true);
            btn.click(() => this.removeForm(el));
            btn.addClass(this.options.rmBtnClass);
            el.append(btn);
        },

        _insertAddBtn: function() {
            /**
             * Inserts an add button which includes a new subform into the main
             * form
             */
            let btn = this.options.addBtnContent;
            btn.click(() => this.addForm());
            btn.addClass(this.options.addBtnClass);
            this.element.append(btn);
            this._addBtn = btn;
        },

        _hideSubform: function(subform) {
            /**
             * Hides a subform without deleting it from the DOM
             * @param  {Node} subform [The subform to be hidden]
             */
            // Remove 'required' constraints for this subform
            $(subform).find('input:required').removeAttr('required')
                      .each((_, entry) => {
                entry.setCustomValidity('');
            });
            $(subform).hide();

        },

        _updateElementIndex: function(el, prefix, ndx) {
            /**
             * Updates the formset indices for a subform
             * @param  {Node}   el     [The subform to be updated]
             * @param  {String} prefix [The form prefix set from Django]
             * @param  {Number} ndx    [The new index value]
             */
            var idRegex = new RegExp(prefix + '-(\\d+|__prefix__)-'),
                replacement = prefix + '-' + ndx + '-';
            if (el.attr("for"))
                el.attr("for", el.attr("for").replace(idRegex, replacement));
            if (el.attr('id'))
                el.attr('id', el.attr('id').replace(idRegex, replacement));
            if (el.attr('name'))
                el.attr('name', el.attr('name').replace(idRegex, replacement));
        },

        _updateFormCount: function() {
            /**
             * Updates the hidden input for the total form count
             */
            let totalForms = $('#id_'+this.options.prefix+'-TOTAL_FORMS');
            totalForms.val(this._numForms);
        },

        _create: function() {
            /**
             * Constructor for the formset widget
             */
            // Hide template form
            this._hideSubform($("#" + this.options.templateId));

            let currForms = this.element.find(this.options.subformSelector);

            // Count existing forms
            this._numForms = this._numActiveForms = currForms.length;

            currForms.each((index, subform) => {
                let delChk = $(subform).find('input:checkbox[id$="-DELETE"]');

                // Replace deletion checkboxes with hidden inputs
                if (delChk.length) {
                    // Remove associated labels, if applicable
                    $('label[for="' + delChk.attr('id') + '"]').hide();

                    const isChecked = delChk.is(':checked');

                    // Change field type
                    delChk[0].type = 'hidden';
                    if (isChecked) {
                        delChk.val('on');
                        $(subform).hide();
                        // Sutract from internal form count
                        --this._numActiveForms;
                    }
                }

                // Insert delete button, if required
                if (this.options.displayControls) {
                    this._insertDeleteBtn($(subform));
                }
            });

            // Insert add button, if required
            if (this.options.displayControls) {
                this._insertAddBtn();
            }

            // Updates the TOTAL_FORMS input, which might be incorrect after a
            // reload
            this._updateFormCount();
        },

        addForm: function() {
            /**
             * Adds a new form from the supplied template.
             */

            // TODO CHECK MAX AND MIN FORMS

            let newForm = $('#' + this.options.templateId).clone(true);
            // Remove original id from the cloned template
            newForm.removeAttr('id');

            // Update sequential numbers
            let self = this;
            newForm.find('input,select,textarea,label,div').each(function() {
                self._updateElementIndex($(this), self.options.prefix,
                                         self._numForms);
            });

            if (this.options.displayControls) {
                this._insertDeleteBtn(
                    newForm.find(this.options.subformSelector)
                );
            }

            this.element.append(newForm);
            newForm.show();

            if (this.options.displayControls) {
                // Update add button position
                $(this._addBtn).insertAfter(newForm);
            }

            // Update internal form count
            ++this._numForms;
            ++this._numActiveForms;

            this._updateFormCount();
        },

        removeForm: function(form) {
            /*
             * Removes a subform from the formset. If it contains a DELETE
             * field, use it to delete the entry in the server, without
             * actually deleting the DOM element for the form.
             * @param  {Node} form [The subform to be removed]
             */

            // TODO CHECK MAX AND MIN FORMS

            // DELETE checkbox selector
            const deleteSel = 'input:hidden[id$="-DELETE"]';

            let deleteForm = form;
            if (!deleteForm) {
                // If no form was supplied, delete the last entry
                let subforms = this.element.find(this.options.subformSelector);

                for (let i = subforms.length - 1; 0 <= i && !deleteForm; i--) {
                    let sub = subforms[i];
                    // Filter out deleted entries
                    if ($(sub).find(deleteSel + '[value="on"]').length == 0) {
                        deleteForm = sub;
                    }
                }
            }

            // Return if there are no forms to remove
            if (!deleteForm) return;

            if ($(deleteForm).find(deleteSel).length) {
                // Mark entry to be deleted in the server-side
                $(deleteForm).find(deleteSel).val('on');
                $(deleteForm).addClass('subform-deleted');
                this._hideSubform(deleteForm);
            } else {
                // Remove entry from formset in the client side
                $(deleteForm).remove();

                --this._numForms;

                this._updateFormCount();

                // Update sequential numbers
                let self = this;
                this.element.find(this.subformSelector).each((index) => {
                    $(this).find('input,select,textarea,label,div')
                           .each(() => {
                        self._updateElementIndex($(this), self.options.prefix,
                                                 index);
                    });
                });
            }

            --this._numActiveForms;
            this._trigger("removed", null, { form: deleteForm } );
        },

        setNumForms: function(n) {
            /*
             * Sets the number of visible forms, adding or removing as
             * required. Hidden forms with the DELETE field set are not taken
             * into account.
             * @param  {Number} n [Number of active forms to be displayed]
             */

            if (n > this._numActiveForms) {
                let toAdd = n - this._numActiveForms;
                for (let i = 0; i < toAdd; i++) this.addForm();
            } else {
                let toRemove = this._numActiveForms - n;
                for (let i = 0; i < toRemove; i++) this.removeForm();
            }
        }
    })
})(jQuery);
