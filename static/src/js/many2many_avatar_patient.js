//import { registry } from "@web/core/registry";
//import {
//    Many2ManyTagsAvatarField,
//    KanbanMany2ManyTagsAvatarField,
//    ListMany2ManyTagsAvatarField,
//} from "@mail/views/web/fields/many2many_avatar_field/many2many_avatar_field";
//import { ModelFieldRelationMixin } from "@web/views/fields/model_field_relation_mixin";
//
//export class Many2ManyTagsAvatarModelField extends ModelFieldRelationMixin(
//    Many2ManyTagsAvatarField
//) {}
//
//export const many2ManyTagsAvatarModelField = {
//    ...many2ManyTagsAvatarField,
//    component: Many2ManyTagsAvatarModelField,
//    additionalClasses: [
//        ...many2ManyTagsAvatarField.additionalClasses,
//        "o_field_many2many_avatar_patient",
//    ],
//    extractProps: (fieldInfo, dynamicInfo) => ({
//        ...many2ManyTagsAvatarField.extractProps(fieldInfo, dynamicInfo),
//        relation: fieldInfo.options?.relation,
//    }),
//};
//
//registry.category("fields").add("many2many_avatar_patient", many2ManyTagsAvatarModelField);
//
//export const kanbanMany2ManyTagsAvatarModelField = {
//    ...KanbanMany2ManyTagsAvatarField,
//    component: KanbanMany2ManyTagsAvatarModelField,
//    additionalClasses: [
//        ...KanbanMany2ManyTagsAvatarField.additionalClasses,
//        "o_field_many2many_avatar_patient",
//    ],
//    extractProps: (fieldInfo, dynamicInfo) => ({
//        ...KanbanMany2ManyTagsAvatarField.extractProps(fieldInfo, dynamicInfo),
//        relation: fieldInfo.options?.relation,
//    }),
//};
//
//registry
//    .category("fields")
//    .add("kanban.many2many_avatar_patient", kanbanMany2ManyTagsAvatarModelField);
//
//export const listMany2ManyTagsAvatarModelField = {
//    ...ListMany2ManyTagsAvatarField,
//    additionalClasses: [
//        ...ListMany2ManyTagsAvatarField.additionalClasses,
//        "o_field_many2many_avatar_patient",
//    ],
//};
//
//registry
//    .category("fields")
//    .add("list.many2many_avatar_patient", listMany2ManyTagsAvatarModelField);
