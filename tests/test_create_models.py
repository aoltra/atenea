# -*- coding: utf-8 -*- 
# docker-compose run web --test-enable --stop-after-init -d test_db -i atenea

from odoo.tests.common import TransactionCase

class TestCreateModels(TransactionCase):
    def setUp(self):
        super(TestCreateModels, self).setUp()

        self.course = self.env['atenea.course'].create({
            'abbr': 'DAM',  
            'name': 'Desarrollo de Aplicaciones Multiplataforma',
        })

        self.rol = self.env['atenea.rol'].create({
            'rol': 'TUT1',  
            'description': 'Tutor de primero de DAM',
            'course_id': self.course.id,
        })

        self.subject = self.env['atenea.subject'].create({
            'abbr': 'PRG',  
            'code': '0147',
            'name': 'Programación',
            'courses_ids': [(4, self.course.id)],    # enlaza con un registro existente de id course.id
            'year': 1
        })

        self.departament = self.env['atenea.departament'].create({
            'name': 'Informática', 
        })

        self.rol_dep = self.env['atenea.rol'].create({
            'rol': 'JEFD',  
            'description': 'Jefe de departamento Informática',
            'departament_id': self.departament.id,
        })

        # modifico un objeto ya creado
        self.course.write({
          'roles_ids':  [(4, self.rol.id)]
        })


    # Los test se ejecutan en orden alfabético
    def test001_new_course(self):
        'Creación de ciclos'
        self.assertEqual(self.course.abbr, 'DAM')
        self.assertEqual(self.course.name, 'Desarrollo de Aplicaciones Multiplataforma')
        self.assertEqual(self.course.subjects_ids[0].abbr, 'PRG')
        self.assertEqual(self.course.roles_ids[0].rol, 'TUT1')
    
    def test002_new_rol(self):
        'Creación de cargos'
        self.assertEqual(self.rol.rol, 'TUT1')
        self.assertEqual(self.rol.course_id.id, self.course.id)

        self.assertEqual(self.rol_dep.rol, 'JEFD')
        self.assertEqual(self.rol_dep.departament_id.id, self.departament.id)

    def test003_new_subject(self):
        'Creación de módulos'
        self.assertEqual(self.subject.abbr, 'PRG')
        self.assertEqual(self.subject.code, '0147')
        self.assertEqual(self.subject.name, 'Programación')
        self.assertEqual(self.subject.courses_ids[0].abbr, 'DAM')
        self.assertEqual(self.subject.year, 1)

    def test004_new_departament(self):
        'Creación de departamentos'
        self.assertEqual(self.departament.name, 'Informática')
        self.assertEqual(self.departament.roles_ids[0].id, self.rol_dep.id)


