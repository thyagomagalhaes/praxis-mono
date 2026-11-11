package app.suasflux.modulo.config;

import java.util.Objects;

import javax.sql.DataSource;

import org.flywaydb.core.Flyway;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.autoconfigure.DataSourceProperties;
import org.springframework.boot.jpa.EntityManagerFactoryBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.DependsOn;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@Configuration
@EnableTransactionManagement
@EnableJpaRepositories(
        basePackages = "app.suasflux.modulo.publico",
        entityManagerFactoryRef = "publicoEntityManagerFactory",
        transactionManagerRef = "publicoTransactionManager"
)
public class PublicoDbConfig {
	
	
    @Bean
    @ConfigurationProperties("app.datasource.publico")
    public DataSourceProperties publicoDataSourceProperties() {
        return new DataSourceProperties();
    }
	
	
    @Bean
    public DataSource publicoDataSource(
            @Qualifier("publicoDataSourceProperties") DataSourceProperties properties) {
        return properties.initializeDataSourceBuilder().build();
    }
	
	
    @Bean
    public Flyway publicoFlyway(
            @Qualifier("publicoDataSource") DataSource dataSource) {
        return Flyway.configure()
                .dataSource(dataSource)
                .locations(
                    "classpath:db/setupschema/publico",
                    "classpath:db/migration/publico",
                    "classpath:db/legacydata/publico"
                )
                .baselineOnMigrate(true)  // Útil para DBs existentes
                .load();
    }
	
	
    @Bean
    @DependsOn("publicoFlyway")  // Garante ordem sem injeção fantasma
    public LocalContainerEntityManagerFactoryBean territorioEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("publicoDataSource") DataSource dataSource) {
        
        return builder
                .dataSource(dataSource)
                .packages("app.suasflux.modulo.publico")
                .persistenceUnit("publico")
                .build();
    }
	

    @Bean
    public PlatformTransactionManager publicoTransactionManager(
            @Qualifier("publicoEntityManagerFactory") 
            LocalContainerEntityManagerFactoryBean entityManagerFactory) {
        
        return new JpaTransactionManager(
            Objects.requireNonNull(entityManagerFactory.getObject(), 
                "EntityManagerFactory não inicializada")
        );
    }
}

