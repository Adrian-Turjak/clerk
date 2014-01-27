
class clerk::django{
    Class['clerk::django::python'] -> Class['clerk::django::install']
    include clerk::django::python
    include clerk::django::install
}

class clerk::django::python{
    package { 'python':
      ensure => present,
      before => Package['python-pip'],
    }
    package { 'python-pip':
      ensure => present,
      require => Package['python'],
    }  
}

class clerk::django::install{
    exec { 'django':
        command => "pip install django==$clerk::djangoversion",
        path => $clerk::aptgetdir,
    }
    exec { 'rest_framework':
        command => "pip install djangorestframework==$clerk::djangorestversion",
        path => $clerk::aptgetdir,
        require => Exec['django'],
    }
    exec { 'mysqldb':
        command => "sudo apt-get install python-mysqldb",
        path => $clerk::aptgetdir,
    }

}
