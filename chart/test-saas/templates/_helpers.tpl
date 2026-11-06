{{/* Name of a component's Deployment and Service: <release>-<component>. */}}
{{- define "test-saas.componentName" -}}
{{- printf "%s-%s" .root.Release.Name .component | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Selector labels; stable across upgrades, so no version in them. */}}
{{- define "test-saas.selectorLabels" -}}
{{- /* quote: release names like "true" or "123" would otherwise render as YAML bool/int. */}}
app.kubernetes.io/name: {{ .root.Chart.Name | quote }}
app.kubernetes.io/instance: {{ .root.Release.Name | quote }}
app.kubernetes.io/component: {{ .component | quote }}
{{- end -}}

{{- define "test-saas.labels" -}}
{{ include "test-saas.selectorLabels" . }}
app.kubernetes.io/version: {{ .root.Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .root.Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .root.Chart.Name .root.Chart.Version }}
{{- end -}}

{{- define "test-saas.image" -}}
{{- printf "%s:%s" .image.repository (default .root.Chart.AppVersion .image.tag) -}}
{{- end -}}

{{/* Restricted pod security: non-root, no privilege escalation, no capabilities. */}}
{{- define "test-saas.podSecurityContext" -}}
runAsNonRoot: true
seccompProfile:
  type: RuntimeDefault
{{- end -}}

{{- define "test-saas.containerSecurityContext" -}}
allowPrivilegeEscalation: false
readOnlyRootFilesystem: true
capabilities:
  drop: ["ALL"]
{{- end -}}
