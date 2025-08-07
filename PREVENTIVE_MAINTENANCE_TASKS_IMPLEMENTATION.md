# Preventive Maintenance Workorder Generation with Tasks

## Overview

This implementation completes the preventive maintenance system by ensuring that when workorders are generated from maintenance schedules, they automatically include tasks from the associated job plans.

## Current System Components

### 1. Asset Maintenance Schedules (`asset.maintenance.schedule`)
- **Purpose**: Defines preventive maintenance schedules for assets
- **Key Fields**:
  - `asset_id`: The asset being maintained
  - `maintenance_type`: Type of maintenance (preventive, corrective, etc.)
  - `job_plan_id`: Associated job plan with tasks
  - `next_maintenance_date`: When the next maintenance is due
  - `interval_number` & `interval_type`: Recurrence pattern

### 2. Job Plans (`maintenance.job.plan`)
- **Purpose**: Templates containing standardized maintenance tasks
- **Structure**:
  - `section_ids`: Sections organizing tasks
  - `task_ids`: All tasks across all sections

### 3. Job Plan Sections (`maintenance.job.plan.section`)
- **Purpose**: Organize tasks into logical groups
- **Fields**:
  - `name`: Section name (e.g., "Safety & Documentation")
  - `sequence`: Order of sections
  - `task_ids`: Tasks in this section

### 4. Job Plan Tasks (`maintenance.job.plan.task`)
- **Purpose**: Individual maintenance tasks
- **Key Fields**:
  - `name`: Task description
  - `description`: Detailed instructions
  - `duration`: Estimated time
  - `tools_materials`: Required tools/materials
  - `responsible_id`: Who should perform the task
  - `product_id`: Required parts
  - `is_checklist_item`: Whether it's a checklist item

### 5. Maintenance Workorders (`maintenance.workorder`)
- **Purpose**: Actual maintenance work orders
- **Key Fields**:
  - `job_plan_id`: Reference to the job plan
  - `section_ids`: Work order sections (copied from job plan)
  - `workorder_task_ids`: Work order tasks (copied from job plan)

### 6. Workorder Sections (`maintenance.workorder.section`)
- **Purpose**: Sections within a work order
- **Fields**:
  - `name`: Section name (copied from job plan)
  - `sequence`: Order (copied from job plan)
  - `task_ids`: Tasks in this section

### 7. Workorder Tasks (`maintenance.workorder.task`)
- **Purpose**: Individual tasks in a work order
- **Key Fields**:
  - `name`: Task description (copied from job plan)
  - `description`: Instructions (copied from job plan)
  - `is_done`: Completion status
  - `notes`: Technician notes
  - `before_image`/`after_image`: Photos
  - All other fields copied from job plan task

## Implementation Details

### 1. Automatic Workorder Generation (`_generate_preventive_workorders`)

**Location**: `asset.maintenance.schedule` model

**Purpose**: Cron job method that automatically generates workorders for due maintenance schedules

**Logic**:
```python
def _generate_preventive_workorders(self):
    today = date.today()
    
    # Find all active preventive maintenance schedules that are due
    due_schedules = self.search([
        ('active', '=', True),
        ('maintenance_type', '=', 'preventive'),
        ('next_maintenance_date', '<=', today),
        ('status', 'in', ['planned', 'done'])
    ])
    
    for schedule in due_schedules:
        work_order = self._create_workorder_with_tasks(schedule)
```

### 2. Workorder Creation with Tasks (`_create_workorder_with_tasks`)

**Purpose**: Creates a workorder and copies tasks from the associated job plan

**Process**:
1. Create the workorder with basic information
2. If a job plan is associated, copy all tasks from the job plan
3. Update the maintenance schedule dates
4. Log the creation

### 3. Task Copying (`_copy_job_plan_tasks_to_workorder`)

**Purpose**: Copies tasks from job plan sections to workorder sections

**Process**:
1. For each job plan section:
   - Create a corresponding workorder section
   - Copy section name and sequence
2. For each task in the job plan section:
   - Create a corresponding workorder task
   - Copy all task details (name, description, duration, etc.)
   - Set `is_done = False` initially

## Cron Job Configuration

**File**: `maintenance_cron.xml`

**Configuration**:
```xml
<record id="ir_cron_advanced_maintenance" model="ir.cron">
    <field name="name">Generate Preventive Maintenance Work Orders</field>
    <field name="model_id" ref="model_asset_maintenance_schedule"/>
    <field name="state">code</field>
    <field name="code">model._generate_preventive_workorders()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
</record>
```

**Schedule**: Runs daily to check for due maintenance schedules

## User Interface

### Workorder Form View

The workorder form includes a "Sections & Tasks" page that displays:

1. **Sections**: Organized groups of tasks
2. **Tasks**: Individual maintenance tasks with:
   - Completion checkbox (`is_done`)
   - Before/after images
   - Technician notes
   - All task details

### Task Management

- **Read-only fields**: Task details copied from job plan (name, description, duration, etc.)
- **Editable fields**: Completion status, notes, images
- **Validation**: Tasks can only be marked complete when workorder is "In Progress"

## Workflow

### 1. Setup Phase
1. Create a job plan with sections and tasks
2. Create an asset maintenance schedule
3. Associate the job plan with the maintenance schedule

### 2. Automatic Generation
1. Cron job runs daily
2. Finds maintenance schedules that are due
3. Generates workorders with tasks copied from job plans
4. Updates maintenance schedule dates

### 3. Execution Phase
1. Technician opens the workorder
2. Views tasks organized by sections
3. Completes tasks and adds notes/images
4. Marks workorder as complete when all tasks are done

## Benefits

1. **Standardization**: All preventive maintenance follows the same job plan structure
2. **Automation**: Workorders are generated automatically with complete task lists
3. **Consistency**: Tasks are copied exactly from job plans, ensuring no missed steps
4. **Traceability**: Complete audit trail of what was done
5. **Efficiency**: Technicians have clear, organized task lists

## Testing

The implementation includes comprehensive testing to verify:

1. **Model existence**: All required models are present
2. **Method existence**: All required methods are implemented
3. **Field existence**: All required fields are defined
4. **Cron job**: The automated generation cron job is configured

## Future Enhancements

1. **Task Dependencies**: Tasks that depend on other tasks being completed first
2. **Conditional Tasks**: Tasks that only appear based on asset condition
3. **Dynamic Task Lists**: Tasks that change based on asset age or usage
4. **Task Templates**: Reusable task templates for common maintenance activities
5. **Mobile Optimization**: Enhanced mobile interface for task completion

## Troubleshooting

### Common Issues

1. **Tasks not appearing**: Check if job plan is associated with maintenance schedule
2. **Cron not running**: Verify cron job is active and properly configured
3. **Tasks not completing**: Ensure workorder is in "In Progress" state
4. **Missing sections**: Verify job plan has sections defined

### Debug Steps

1. Check maintenance schedule has a job plan assigned
2. Verify job plan has sections and tasks
3. Test manual workorder generation
4. Check cron job logs for errors
5. Verify workorder form view displays tasks correctly